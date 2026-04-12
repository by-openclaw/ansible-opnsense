#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense traffic shaper rule management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ts_rule
short_description: Manage OPNsense traffic shaper rules
version_added: "0.3.0"
description:
  - Create, update, or delete traffic shaper rule entries on OPNsense.
  - Thin wrapper around lib-opnsense TsRuleManager.ensure().
  - Requires OPNsense >= 26.1.
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
    description: Rule description (part of composite match key).
    type: str
    required: true
  interface:
    description: Interface to apply the rule on (part of composite match key).
    type: str
    required: true
  proto:
    description: Protocol filter (part of composite match key).
    type: str
    choices: [ip, ip4, ip6, udp, tcp]
    default: ip
  direction:
    description: Traffic direction.
    type: str
    choices: ["", in, out]
    default: ""
  enabled:
    description: Whether the rule is enabled.
    type: bool
    default: true
  sequence:
    description: Rule sequence number.
    type: int
  src_port:
    description: Source port or port range.
    type: str
    default: ""
  dst_port:
    description: Destination port or port range.
    type: str
    default: ""
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
- name: Create a traffic shaper rule
  by_systems.opnsense.opnsense_ts_rule:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Limit HTTP on LAN"
    interface: lan
    proto: tcp
    direction: in
    dst_port: "80"
    sequence: 10
    state: present

- name: Remove a traffic shaper rule
  by_systems.opnsense.opnsense_ts_rule:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Limit HTTP on LAN"
    interface: lan
    proto: tcp
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
            "interface": {"type": "str", "required": True},
            "proto": {
                "type": "str",
                "choices": ["ip", "ip4", "ip6", "udp", "tcp"],
                "default": "ip",
            },
            "direction": {
                "type": "str",
                "choices": ["", "in", "out"],
                "default": "",
            },
            "enabled": {"type": "bool", "default": True},
            "sequence": {"type": "int"},
            "src_port": {"type": "str", "default": ""},
            "dst_port": {"type": "str", "default": ""},
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
        "proto": module.params["proto"],
        "enabled": "1" if module.params["enabled"] else "0",
    }
    if module.params["direction"]:
        params["direction"] = module.params["direction"]
    if module.params["sequence"] is not None:
        params["sequence"] = str(module.params["sequence"])
    if module.params["src_port"]:
        params["src_port"] = module.params["src_port"]
    if module.params["dst_port"]:
        params["dst_port"] = module.params["dst_port"]

    from opnsense.managers.shaper.ts_rule import TsRuleManager

    run_module(module, TsRuleManager, params)


if __name__ == "__main__":
    main()
