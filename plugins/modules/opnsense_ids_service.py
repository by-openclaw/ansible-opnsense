#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_ids_service — thin wrapper on lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ids_service
short_description: Control the OPNsense Suricata IDS service and refresh its rules
version_added: "0.5.0"
description:
  - >
    Start, stop or reconfigure Suricata — lib-opnsense IdsServiceManager.ensure(); C(rules_updated) downloads the enabled rulesets (C(updateRules), long-running, always reports changed).
  - C(reconfigured) and C(rules_updated) always apply and are therefore never idempotent by design.
options:
  host:
    description: OPNsense hostname or IP address.
    type: str
    required: true
  key:
    description: OPNsense API key.
    type: str
    required: true
    no_log: true
  secret:
    description: OPNsense API secret.
    type: str
    required: true
    no_log: true
  port:
    description: OPNsense HTTPS port.
    type: int
    default: 443
  verify_ssl:
    description: Verify TLS certificate.
    type: bool
    default: false
  state:
    description: Target state.
    type: str
    choices: [running, stopped, reconfigured, rules_updated]
    default: running
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Fetch the enabled rulesets then make sure Suricata runs
  by_systems.opnsense.opnsense_ids_service:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    state: rules_updated

- by_systems.opnsense.opnsense_ids_service:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    state: running
"""

RETURN = r"""
changed:
  description: Whether state on the firewall was modified.
  type: bool
  returned: always
action:
  description: One of C(started), C(stopped), C(restarted), C(reconfigured), C(rules_updated) or C(noop).
  type: str
  returned: always
diff:
  description: Before/after state.
  type: dict
  returned: when changed
"""

from ansible.module_utils.basic import AnsibleModule

try:
    from ansible_collections.by_systems.opnsense.plugins.module_utils.opnsense_helper import (
        opn_argument_spec,
        run_module,
    )
except ImportError:
    from plugins.module_utils.opnsense_helper import opn_argument_spec, run_module


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update(
        {
            "state": {
                "type": "str",
                "choices": ["running", "stopped", "reconfigured", "rules_updated"],
                "default": "running",
            }
        }
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    from opnsense.managers.ids.service import IdsServiceManager

    if module.params["state"] == "rules_updated":
        import asyncio

        from opnsense.client import OpnsenseClient

        async def _update() -> None:
            if module.check_mode:
                module.exit_json(changed=True, action="rules_updated", uuid="", diff={})
            async with OpnsenseClient(
                host=module.params["host"],
                key=module.params["key"],
                secret=module.params["secret"],
                port=module.params["port"],
                verify_ssl=module.params["verify_ssl"],
            ) as client:
                await IdsServiceManager(client).update_rules()
                module.exit_json(changed=True, action="rules_updated", uuid="", diff={})

        asyncio.run(_update())
        return

    run_module(module, IdsServiceManager, {})


if __name__ == "__main__":
    main()
