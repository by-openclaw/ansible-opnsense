#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_ids_ruleset — thin wrapper on lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ids_ruleset
short_description: Enable / disable OPNsense Suricata rulesets by filename
version_added: "0.5.0"
description:
  - >
    Toggle downloadable IDS rulesets (the fixed catalogue from C(listRulesets): 48 ET Open C(emerging-*.rules), abuse.ch, OPNsense app-detect…) — lib-opnsense IdsRulesetManager.ensure_many(); only drifted sets are toggled.
  - >
    I(rulesets) maps filename → enabled; I(enable_prefix) enables every ruleset whose filename starts with the given prefixes (e.g. C(emerging-) for all ET Open).
  - >
    Toggling only flags a set — fetch the rules with M(by_systems.opnsense.opnsense_ids_service) C(state=rules_updated). A seeded device with I(interfaces)=wan in its IDS settings refuses every save: apply M(by_systems.opnsense.opnsense_ids_settings) first.
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
  rulesets:
    description: Filename → enabled map, e.g. C(abuse.ch.sslblacklist.rules) → C(true).
    type: dict
  enable_prefix:
    description: Enable every catalogue ruleset whose filename starts with one of these prefixes.
    type: list
    elements: str
  disable_others:
    description: Disable every catalogue ruleset not covered by I(rulesets) / I(enable_prefix).
    type: bool
    default: false
  apply:
    description: Reconfigure the IDS after toggling.
    type: bool
    default: true
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: ET Open + abuse.ch SSL blocklists on, everything else off
  by_systems.opnsense.opnsense_ids_ruleset:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    enable_prefix: [emerging-]
    rulesets:
      abuse.ch.sslblacklist.rules: true
      abuse.ch.sslipblacklist.rules: true
    disable_others: true
"""

RETURN = r"""
changed:
  description: Whether state on the firewall was modified.
  type: bool
  returned: always
action:
  description: One of C(updated) or C(noop).
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
            "rulesets": {"type": "dict"},
            "enable_prefix": {"type": "list", "elements": "str"},
            "disable_others": {"type": "bool", "default": False},
            "apply": {"type": "bool", "default": True},
        }
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    import asyncio

    from opnsense.client import OpnsenseClient
    from opnsense.exceptions import OpnsenseError
    from opnsense.managers.ids.ruleset import IdsRulesetManager

    async def _run() -> None:
        async with OpnsenseClient(
            host=module.params["host"],
            key=module.params["key"],
            secret=module.params["secret"],
            port=module.params["port"],
            verify_ssl=module.params["verify_ssl"],
        ) as client:
            mgr = IdsRulesetManager(client)
            catalogue = [r["filename"] for r in await mgr.list()]
            desired: dict = {}
            for prefix in module.params.get("enable_prefix") or []:
                for name in catalogue:
                    if name.startswith(prefix):
                        desired[name] = True
            for name, flag in (module.params.get("rulesets") or {}).items():
                desired[str(name)] = (
                    bool(flag)
                    if not isinstance(flag, str)
                    else flag.lower() in ("1", "true", "yes", "on")
                )
            if module.params["disable_others"]:
                for name in catalogue:
                    desired.setdefault(name, False)
            if not desired:
                module.fail_json(
                    msg="opnsense_ids_ruleset: nothing to ensure — set rulesets and/or enable_prefix"
                )
            r = await mgr.ensure_many(
                desired, check_mode=module.check_mode, apply=module.params["apply"]
            )
            diff = {"before": r.before, "after": r.after} if r.changed else {}
            module.exit_json(changed=r.changed, action=r.action, uuid="", diff=diff)

    try:
        asyncio.run(_run())
    except OpnsenseError as exc:
        module.fail_json(msg=str(exc))
    except ValueError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
