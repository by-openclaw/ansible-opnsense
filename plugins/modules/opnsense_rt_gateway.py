#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense gateway management."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_rt_gateway
short_description: Manage OPNsense gateways
version_added: "0.2.0"
description:
  - Create, update, or delete gateways on OPNsense.
  - Thin wrapper around lib-opnsense RtGatewayManager.ensure().
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
    description: OPNsense API port.
    type: int
    default: 443
  verify_ssl:
    description: Verify SSL certificate.
    type: bool
    default: false
  name:
    description: Gateway name (match key).
    type: str
    required: true
  interface:
    description: Network interface.
    type: str
    required: true
  gateway:
    description: Gateway IP address.
    type: str
    required: true
  ipprotocol:
    description: IP protocol version.
    type: str
    choices: [inet, inet6]
    default: inet
  disabled:
    description: Disable this gateway.
    type: bool
    default: false
  defaultgw:
    description: Mark as default gateway.
    type: bool
    default: false
  priority:
    description: Gateway priority (0-255).
    type: int
  weight:
    description: Gateway weight for load balancing (1-5).
    type: int
  fargw:
    description: Far gateway (non-local gateway).
    type: bool
    default: false
  monitor_disable:
    description: Disable gateway monitoring.
    type: bool
    default: false
  monitor:
    description: Monitor IP address.
    type: str
    default: ""
  state:
    description: Desired state of the gateway.
    type: str
    choices: [present, absent]
    default: present
requirements:
  - lib-opnsense >= 1.0.0
author:
  - BY-SYSTEMS (@by-openclaw)
"""

EXAMPLES = r"""
- name: Create gateway
  by_systems.opnsense.opnsense_rt_gateway:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: inttest-gw-wan
    interface: wan
    gateway: 10.1.1.1
    state: present

- name: Delete gateway
  by_systems.opnsense.opnsense_rt_gateway:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: inttest-gw-wan
    interface: wan
    gateway: 10.1.1.1
    state: absent
"""

RETURN = r"""
changed:
  description: Whether the resource was changed.
  type: bool
  returned: always
action:
  description: Action taken (created, updated, deleted, noop).
  type: str
  returned: always
uuid:
  description: UUID of the resource.
  type: str
  returned: when available
diff:
  description: Before/after state when changed.
  type: dict
  returned: when changed
"""

try:
    from ansible_collections.by_systems.opnsense.plugins.module_utils.opnsense_helper import (
        opn_argument_spec,
        run_module,
    )
except ImportError:
    from plugins.module_utils.opnsense_helper import opn_argument_spec, run_module

from ansible.module_utils.basic import AnsibleModule


def main() -> None:
    spec = opn_argument_spec()
    spec.update(
        {
            "name": {"type": "str", "required": True},
            "interface": {"type": "str", "required": True},
            "gateway": {"type": "str", "required": True},
            "ipprotocol": {
                "type": "str",
                "choices": ["inet", "inet6"],
                "default": "inet",
            },
            "disabled": {"type": "bool", "default": False},
            "defaultgw": {"type": "bool", "default": False},
            "priority": {"type": "int"},
            "weight": {"type": "int"},
            "fargw": {"type": "bool", "default": False},
            "monitor_disable": {"type": "bool", "default": False},
            "monitor": {"type": "str", "default": ""},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {
        "name": module.params["name"],
        "interface": module.params["interface"],
        "gateway": module.params["gateway"],
        "ipprotocol": module.params["ipprotocol"],
        "disabled": "1" if module.params["disabled"] else "0",
        "defaultgw": "1" if module.params["defaultgw"] else "0",
        "fargw": "1" if module.params["fargw"] else "0",
        "monitor_disable": "1" if module.params["monitor_disable"] else "0",
    }
    if module.params["priority"] is not None:
        params["priority"] = str(module.params["priority"])
    if module.params["weight"] is not None:
        params["weight"] = str(module.params["weight"])
    if module.params["monitor"]:
        params["monitor"] = module.params["monitor"]

    from opnsense.managers.routing.gateway import RtGatewayManager

    run_module(module, RtGatewayManager, params)


if __name__ == "__main__":
    main()
