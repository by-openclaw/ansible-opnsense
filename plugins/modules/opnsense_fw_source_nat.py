#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense source NAT rule management."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_fw_source_nat
short_description: Manage OPNsense source NAT rules
version_added: "0.2.0"
description:
  - Create, update, or delete source NAT rules on OPNsense.
  - Thin wrapper around lib-opnsense FwSourceNatManager.ensure().
  - Requires OPNsense >= 25.1.
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
  description:
    description: Rule description (used as unique identifier for matching).
    type: str
    required: true
  interface:
    description: Interface to apply the rule on.
    type: str
    default: wan
  ipprotocol:
    description: IP protocol version.
    type: str
    choices: [inet, inet6]
    default: inet
  protocol:
    description: Transport protocol.
    type: str
    default: any
  source_net:
    description: Source network or alias.
    type: str
    default: any
  source_port:
    description: Source port or port range.
    type: str
    default: ""
  destination_net:
    description: Destination network or alias.
    type: str
    default: any
  destination_port:
    description: Destination port or port range.
    type: str
    default: ""
  target:
    description: >
      NAT target — the address to rewrite the source to.
      Common values: wanip, interface IP, or a specific address.
    type: str
    default: wanip
  enabled:
    description: Whether the rule is enabled.
    type: bool
    default: true
  log:
    description: Log matching packets.
    type: bool
    default: false
  state:
    description: Desired state of the rule.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Masquerade DMZ to WAN
  by_systems.opnsense.opnsense_fw_source_nat:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Masquerade DMZ to WAN"
    interface: wan
    source_net: "10.6.225.0/24"
    target: wanip
    state: present

- name: Remove a source NAT rule
  by_systems.opnsense.opnsense_fw_source_nat:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Old SNAT rule"
    state: absent
"""

RETURN = r"""
changed:
  description: Whether the module made any changes.
  type: bool
  returned: always
action:
  description: Action performed — created, updated, deleted, or noop.
  type: str
  returned: always
uuid:
  description: UUID of the affected resource.
  type: str
  returned: when available
diff:
  description: Before/after state for audit trail.
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
            "description": {"type": "str", "required": True},
            "interface": {"type": "str", "default": "wan"},
            "ipprotocol": {
                "type": "str",
                "choices": ["inet", "inet6"],
                "default": "inet",
            },
            "protocol": {"type": "str", "default": "any"},
            "source_net": {"type": "str", "default": "any"},
            "source_port": {"type": "str", "default": ""},
            "destination_net": {"type": "str", "default": "any"},
            "destination_port": {"type": "str", "default": ""},
            "target": {"type": "str", "default": "wanip"},
            "enabled": {"type": "bool", "default": True},
            "log": {"type": "bool", "default": False},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {
        "description": module.params["description"],
        "interface": module.params["interface"],
        "ipprotocol": module.params["ipprotocol"],
        "protocol": module.params["protocol"],
        "source_net": module.params["source_net"],
        "destination_net": module.params["destination_net"],
        "target": module.params["target"],
        "enabled": "1" if module.params["enabled"] else "0",
        "log": "1" if module.params["log"] else "0",
    }
    if module.params["source_port"]:
        params["source_port"] = module.params["source_port"]
    if module.params["destination_port"]:
        params["destination_port"] = module.params["destination_port"]

    from opnsense.managers.firewall.source_nat import FwSourceNatManager

    run_module(module, FwSourceNatManager, params)


if __name__ == "__main__":
    main()
