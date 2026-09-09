#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense WireGuard server management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_wg_server
short_description: Manage OPNsense WireGuard server instances
version_added: "0.3.0"
description:
  - Create, update, or delete WireGuard server instances on OPNsense.
  - Thin wrapper around lib-opnsense WgServerManager.ensure().
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
  name:
    description: WireGuard server name (unique identifier).
    type: str
    required: true
  enabled:
    description: Whether the server instance is enabled.
    type: bool
    default: true
  listen_port:
    description: WireGuard listen port.
    type: int
  mtu:
    description: Tunnel MTU.
    type: int
  tunneladdress:
    description: Tunnel address (CIDR notation).
    type: str
    default: ""
  dns:
    description: DNS server for the tunnel.
    type: str
    default: ""
  disableroutes:
    description: Disable automatic route installation.
    type: bool
    default: false
  gateway:
    description: Gateway for the tunnel.
    type: str
    default: ""
  peers:
    description: Comma-separated list of peer UUIDs.
    type: str
    default: ""
  state:
    description: Desired state of the server instance.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create a WireGuard server
  by_systems.opnsense.opnsense_wg_server:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: wg0
    listen_port: 51820
    tunneladdress: "10.10.10.1/24"
    state: present

- name: Remove a WireGuard server
  by_systems.opnsense.opnsense_wg_server:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: wg0
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
            "name": {"type": "str", "required": True},
            "enabled": {"type": "bool", "default": True},
            "listen_port": {"type": "int"},
            "mtu": {"type": "int"},
            "tunneladdress": {"type": "str", "default": ""},
            "dns": {"type": "str", "default": ""},
            "disableroutes": {"type": "bool", "default": False},
            "gateway": {"type": "str", "default": ""},
            "peers": {"type": "str", "default": ""},
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
        "enabled": "1" if module.params["enabled"] else "0",
        "disableroutes": "1" if module.params["disableroutes"] else "0",
    }
    if module.params["listen_port"] is not None:
        params["port"] = str(module.params["listen_port"])
    if module.params["mtu"] is not None:
        params["mtu"] = str(module.params["mtu"])
    if module.params["tunneladdress"]:
        params["tunneladdress"] = module.params["tunneladdress"]
    if module.params["dns"]:
        params["dns"] = module.params["dns"]
    if module.params["gateway"]:
        params["gateway"] = module.params["gateway"]
    if module.params["peers"]:
        params["peers"] = module.params["peers"]

    from opnsense.managers.vpn.wg_server import WgServerManager

    run_module(module, WgServerManager, params)


if __name__ == "__main__":
    main()
