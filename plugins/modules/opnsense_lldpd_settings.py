#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module for OPNsense os-lldpd general settings via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_lldpd_settings
short_description: Manage OPNsense LLDP daemon (os-lldpd) general settings
version_added: "0.5.0"
description:
  - Manage the general settings of the os-lldpd plugin.
  - Thin wrapper around lib-opnsense LldpdGeneralManager.ensure().
  - Announce on internal interfaces only — never the WAN uplinks.
  - Only the options you set are diffed and sent — everything else is left untouched.
  - Requires OPNsense >= 26.1 and the os-lldpd plugin.
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
  enabled:
    description: Enable lldpd.
    type: bool
  cdp:
    description: Also speak CDP (Cisco).
    type: bool
  fdp:
    description: Also speak FDP (Foundry).
    type: bool
  edp:
    description: Also speak EDP (Extreme).
    type: bool
  sonmp:
    description: Also speak SONMP (Nortel).
    type: bool
  agentx:
    description: Expose an SNMP AgentX sub-agent.
    type: bool
  interfaces:
    description: Interface slot ids to announce on (API field C(interface), CSV).
    type: list
    elements: str
  state:
    description: Only C(present) is supported (singleton settings).
    type: str
    choices: [present]
    default: present
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Manage OPNsense LLDP daemon (os-lldpd) general settings
  by_systems.opnsense.opnsense_lldpd_settings:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    enabled: true
    interfaces: [lan, opt1, opt2]
    cdp: false
"""

RETURN = r"""
changed:
  description: Whether any setting drifted.
  type: bool
  returned: always
action:
  description: One of C(updated) or C(noop).
  type: str
  returned: always
diff:
  description: Before/after settings.
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

# API booleans are the strings "0"/"1", not JSON booleans.
_BOOL_FIELDS = ("enabled", "cdp", "fdp", "edp", "sonmp", "agentx")
_STR_FIELDS = ()
# Multi-selects: the manager normalises a list to the CSV the API expects.
_LIST_FIELDS = ("interfaces",)
# Module option -> API field (only where they differ).
_API_NAMES = {"interfaces": "interface"}


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update({f: {"type": "bool"} for f in _BOOL_FIELDS})
    spec.update({f: {"type": "str"} for f in _STR_FIELDS})
    spec.update({f: {"type": "list", "elements": "str"} for f in _LIST_FIELDS})
    spec.update(
        {"state": {"type": "str", "choices": ["present"], "default": "present"}}
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    # Only send what the caller actually set: the manager diffs solely the keys
    # it receives, so an unset option leaves that setting untouched.
    params: dict = {}
    for field in _BOOL_FIELDS:
        if module.params.get(field) is not None:
            params[_API_NAMES.get(field, field)] = "1" if module.params[field] else "0"
    for field in _STR_FIELDS:
        if module.params.get(field) is not None:
            params[_API_NAMES.get(field, field)] = module.params[field]
    for field in _LIST_FIELDS:
        if module.params.get(field) is not None:
            params[_API_NAMES.get(field, field)] = list(module.params[field])

    from opnsense.managers.services.lldpd_general import LldpdGeneralManager

    run_module(module, LldpdGeneralManager, params)


if __name__ == "__main__":
    main()
