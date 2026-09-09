#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense D-NAT (port forward) rule management."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_fw_dnat
short_description: Manage OPNsense D-NAT / port forward rules
version_added: "0.2.0"
description:
  - Create, update, or delete D-NAT (port forward) rules on OPNsense.
  - Thin wrapper around lib-opnsense FwDnatManager.ensure().
  - Requires OPNsense >= 26.1 (D-NAT was legacy PHP before that).
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
  dedupe:
    description:
      - >
        Collapse several resources that carry the same identity keys instead of failing.
        Without it a duplicate makes the task fail with an ambiguous-match error, because the
        module will not guess which copy the catalog meant. With it the lowest-UUID copy
        survives and converges and the rest are deleted.
      - Off by default — deleting is never a silent default.
    type: bool
    default: false
  descr:
    description: >
      Rule description (used as unique identifier for matching).
      Note: D-NAT uses 'descr' not 'description'.
    type: str
    required: true
  interface:
    description: Interface to apply the rule on.
    type: str
    default: wan
  ipprotocol:
    description: IP protocol version.
    type: str
    choices: ["", inet, inet6, inet46]
    default: inet
  protocol:
    description: Transport protocol.
    type: str
    default: tcp
  target:
    description: Internal target IP address for the port forward.
    type: str
    required: true
  local_port:
    description: Internal target port.
    type: str
    default: ""
  source_net:
    description: Source network/host (alias name, CIDR, C(any)). Empty = any.
    type: str
    default: ""
  source_port:
    description: Source port (alias name, number or range). Empty = any.
    type: str
    default: ""
  source_not:
    description: Invert the source match.
    type: bool
    default: false
  destination_net:
    description: >
      Destination network/host to match — for a port forward this is the WAN
      address: an alias name, C(wanip), an interface address keyword such as
      C(opt12ip), or a CIDR. Empty = any.
    type: str
    default: ""
  destination_port:
    description: Destination (external) port to match — alias name, number or range.
    type: str
    default: ""
  destination_not:
    description: Invert the destination match.
    type: bool
    default: false
  sequence:
    description: Rule order (lower first). Empty = OPNsense default placement.
    type: int
  natreflection:
    description: NAT reflection mode for this rule.
    type: str
    choices: ["", purenat, disable]
    default: ""
  nordr:
    description: No RDR (disable redirect, e.g. for exclusions).
    type: bool
    default: false
  disabled:
    description: Whether the rule is disabled.
    type: bool
    default: false
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
notes:
  - D-NAT requires OPNsense >= 26.1. On older versions this module will
    fail with a 404 endpoint error.
"""

EXAMPLES = r"""
- name: Forward HTTPS to web server
  by_systems.opnsense.opnsense_fw_dnat:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    descr: "Forward HTTPS to web-01"
    interface: wan
    protocol: tcp
    target: "10.6.225.10"
    local_port: "443"
    destination_net: host4_wan_pub
    destination_port: port_https
    sequence: 10
    state: present

- name: Remove a port forward
  by_systems.opnsense.opnsense_fw_dnat:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    descr: "Old port forward"
    target: "10.6.225.99"
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
            "descr": {"type": "str", "required": True},
            "interface": {"type": "str", "default": "wan"},
            "ipprotocol": {
                "type": "str",
                "choices": ["", "inet", "inet6", "inet46"],
                "default": "inet",
            },
            "protocol": {"type": "str", "default": "tcp"},
            "target": {"type": "str", "required": True},
            "local_port": {"type": "str", "default": ""},
            "source_net": {"type": "str", "default": ""},
            "source_port": {"type": "str", "default": ""},
            "source_not": {"type": "bool", "default": False},
            "destination_net": {"type": "str", "default": ""},
            "destination_port": {"type": "str", "default": ""},
            "destination_not": {"type": "bool", "default": False},
            "sequence": {"type": "int"},
            "natreflection": {
                "type": "str",
                "choices": ["", "purenat", "disable"],
                "default": "",
            },
            "nordr": {"type": "bool", "default": False},
            "disabled": {"type": "bool", "default": False},
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
        "descr": module.params["descr"],
        "interface": module.params["interface"],
        "ipprotocol": module.params["ipprotocol"],
        "protocol": module.params["protocol"],
        "target": module.params["target"],
        "disabled": "1" if module.params["disabled"] else "0",
        "log": "1" if module.params["log"] else "0",
    }
    if module.params["local_port"]:
        params["local-port"] = module.params["local_port"]
    src = {
        k: v
        for k, v in {
            "network": module.params["source_net"],
            "port": module.params["source_port"],
            "not": "1" if module.params["source_not"] else "",
        }.items()
        if v
    }
    if src:
        params["source"] = src
    dst = {
        k: v
        for k, v in {
            "network": module.params["destination_net"],
            "port": module.params["destination_port"],
            "not": "1" if module.params["destination_not"] else "",
        }.items()
        if v
    }
    if dst:
        params["destination"] = dst
    if module.params["sequence"] is not None:
        params["sequence"] = module.params["sequence"]
    if module.params["natreflection"]:
        params["natreflection"] = module.params["natreflection"]
    if module.params["nordr"]:
        params["nordr"] = "1"

    from opnsense.managers.firewall.dnat import FwDnatManager

    run_module(module, FwDnatManager, params)


if __name__ == "__main__":
    main()
