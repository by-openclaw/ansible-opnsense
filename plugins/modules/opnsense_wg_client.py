#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense WireGuard client (peer) management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_wg_client
short_description: Manage OPNsense WireGuard clients (peers)
version_added: "0.3.0"
description:
  - Create, update, or delete WireGuard client (peer) entries on OPNsense.
  - Thin wrapper around lib-opnsense WgClientManager.ensure().
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
  name:
    description: Client (peer) name (unique identifier).
    type: str
    required: true
  enabled:
    description: Whether the client is enabled.
    type: bool
    default: true
  pubkey:
    description: WireGuard public key.
    type: str
    default: ""
    no_log: true
  psk:
    description: Pre-shared key.
    type: str
    default: ""
    no_log: true
  tunneladdress:
    description: Allowed IPs / tunnel address (CIDR).
    type: str
    default: ""
  serveraddress:
    description: Server endpoint address.
    type: str
    default: ""
  serverport:
    description: Server endpoint port.
    type: int
  keepalive:
    description: Persistent keepalive interval in seconds.
    type: int
    default: 0
  endpoint:
    description: Endpoint override.
    type: str
    default: ""
  state:
    description: Desired state of the client.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create a WireGuard peer
  by_systems.opnsense.opnsense_wg_client:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: peer1
    pubkey: "aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789+abc="
    tunneladdress: "10.10.10.2/32"
    serveraddress: "vpn.example.com"
    serverport: 51820
    keepalive: 25
    state: present

- name: Remove a WireGuard peer
  by_systems.opnsense.opnsense_wg_client:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: peer1
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
            "pubkey": {"type": "str", "default": "", "no_log": True},
            "psk": {"type": "str", "default": "", "no_log": True},
            "tunneladdress": {"type": "str", "default": ""},
            "serveraddress": {"type": "str", "default": ""},
            "serverport": {"type": "int"},
            "keepalive": {"type": "int", "default": 0},
            "endpoint": {"type": "str", "default": ""},
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
        "keepalive": str(module.params["keepalive"]),
    }
    if module.params["pubkey"]:
        params["pubkey"] = module.params["pubkey"]
    if module.params["psk"]:
        params["psk"] = module.params["psk"]
    if module.params["tunneladdress"]:
        params["tunneladdress"] = module.params["tunneladdress"]
    if module.params["serveraddress"]:
        params["serveraddress"] = module.params["serveraddress"]
    if module.params["serverport"] is not None:
        params["serverport"] = str(module.params["serverport"])
    if module.params["endpoint"]:
        params["endpoint"] = module.params["endpoint"]

    from opnsense.managers.vpn.wg_client import WgClientManager

    run_module(module, WgClientManager, params)


if __name__ == "__main__":
    main()
