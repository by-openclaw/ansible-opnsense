#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_radvd_entry — thin wrapper on lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_radvd_entry
short_description: Manage OPNsense radvd per-interface router advertisement entries
version_added: "0.5.0"
description:
  - CRUD for radvd entries (matched by I(interface)) — lib-opnsense RadvdEntryManager.ensure().
  - Kea DHCPv6 emits no router advertisements; one entry per served interface is required.
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
  interface:
    description: Interface slot id (match key).
    type: str
    required: true
  enabled:
    description: Enable the entry.
    type: bool
  mode:
    description: Advertisement mode.
    type: str
    choices: [router, unmanaged, managed, assist, stateless]
  base6_interface:
    description: Track this interface's prefix (API field C(Base6Interface)).
    type: str
  deprecate_prefix:
    description: Deprecate the prefix on change (C(on)/C(off), empty = default).
    type: str
    choices: ["", "on", "off"]
  remove_adv_on_exit:
    description: Withdraw advertisements on exit (API field C(RemoveAdvOnExit)).
    type: str
    choices: ["", "on", "off"]
  remove_route:
    description: Remove the route on exit (API field C(RemoveRoute)).
    type: str
    choices: ["", "on", "off"]
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Unmanaged RAs on the MGMT VLAN (Kea6 hands out addresses)
  by_systems.opnsense.opnsense_radvd_entry:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    interface: opt2
    mode: unmanaged
    enabled: true
"""

RETURN = r"""
changed:
  description: Whether state on the firewall was modified.
  type: bool
  returned: always
action:
  description: One of C(created), C(updated), C(deleted) or C(noop).
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


_API_NAMES = {
    "base6_interface": "Base6Interface",
    "deprecate_prefix": "DeprecatePrefix",
    "remove_adv_on_exit": "RemoveAdvOnExit",
    "remove_route": "RemoveRoute",
}


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update(
        {
            "interface": {"type": "str", "required": True},
            "enabled": {"type": "bool"},
            "mode": {
                "type": "str",
                "choices": ["router", "unmanaged", "managed", "assist", "stateless"],
            },
            "base6_interface": {"type": "str"},
            "deprecate_prefix": {"type": "str", "choices": ["", "on", "off"]},
            "remove_adv_on_exit": {"type": "str", "choices": ["", "on", "off"]},
            "remove_route": {"type": "str", "choices": ["", "on", "off"]},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {"interface": module.params["interface"]}
    if module.params.get("enabled") is not None:
        params["enabled"] = "1" if module.params["enabled"] else "0"
    for field in (
        "mode",
        "base6_interface",
        "deprecate_prefix",
        "remove_adv_on_exit",
        "remove_route",
    ):
        if module.params.get(field) is not None:
            params[_API_NAMES.get(field, field)] = module.params[field]

    from opnsense.managers.services.radvd_entry import RadvdEntryManager

    run_module(module, RadvdEntryManager, params)


if __name__ == "__main__":
    main()
