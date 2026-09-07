#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_ddns_service — thin wrapper on lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ddns_service
short_description: Control the OPNsense Dynamic DNS (os-ddclient) service
version_added: "0.5.0"
description:
  - >
    Start, stop, restart or reconfigure the Dynamic DNS (os-ddclient) service — lib-opnsense DdnsServiceManager.ensure().
  - A C(restart) after an account change makes ddclient publish the active WAN address immediately.
  - C(reconfigured) and C(restarted) always apply and are therefore never idempotent by design.
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
    description: Target service state.
    type: str
    choices: [running, stopped, restarted, reconfigured]
    default: reconfigured
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Apply the Dynamic DNS (os-ddclient) configuration
  by_systems.opnsense.opnsense_ddns_service:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    state: reconfigured
"""

RETURN = r"""
changed:
  description: Whether state on the firewall was modified.
  type: bool
  returned: always
action:
  description: One of C(started), C(stopped), C(restarted), C(reconfigured) or C(noop).
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
                "choices": ["running", "stopped", "restarted", "reconfigured"],
                "default": "reconfigured",
            }
        }
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    from opnsense.managers.services.ddns_service import DdnsServiceManager

    if module.params["state"] == "restarted":
        # BaseServiceManager.ensure() has no 'restarted' state; call the action directly.
        import asyncio

        from opnsense.client import OpnsenseClient

        async def _restart() -> None:
            async with OpnsenseClient(
                host=module.params["host"],
                key=module.params["key"],
                secret=module.params["secret"],
                port=module.params["port"],
                verify_ssl=module.params["verify_ssl"],
            ) as client:
                r = await DdnsServiceManager(client).restart(
                    check_mode=module.check_mode
                )
                module.exit_json(
                    changed=r.changed,
                    action=r.action,
                    uuid="",
                    diff={"before": r.before, "after": r.after},
                )

        asyncio.run(_restart())
        return

    run_module(module, DdnsServiceManager, {})


if __name__ == "__main__":
    main()
