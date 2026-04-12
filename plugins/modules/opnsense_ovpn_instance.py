#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense OpenVPN instance management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ovpn_instance
short_description: Manage OPNsense OpenVPN instances
version_added: "0.3.0"
description:
  - Create, update, or delete OpenVPN server or client instances on OPNsense.
  - Thin wrapper around lib-opnsense OvpnInstanceManager.ensure().
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
    description: Instance description (unique identifier).
    type: str
    required: true
  enabled:
    description: Whether the instance is enabled.
    type: bool
    default: true
  role:
    description: Instance role.
    type: str
    choices: [server, client]
    default: server
  dev_type:
    description: Device type (tun or tap).
    type: str
    default: ""
  proto:
    description: Protocol (UDP, UDP4, UDP6, TCP, TCP4, TCP6).
    type: str
    default: ""
  listen_port:
    description: Listen port for the instance.
    type: int
  server:
    description: Server network (CIDR notation).
    type: str
    default: ""
  cert:
    description: Certificate reference UUID.
    type: str
    default: ""
  ca:
    description: CA reference UUID.
    type: str
    default: ""
  local:
    description: Local bind address.
    type: str
    default: ""
  remote:
    description: Remote server address (client mode).
    type: str
    default: ""
  keepalive_interval:
    description: Keepalive ping interval.
    type: str
    default: ""
  keepalive_timeout:
    description: Keepalive timeout.
    type: str
    default: ""
  tun_mtu:
    description: Tunnel MTU.
    type: str
    default: ""
  maxclients:
    description: Maximum number of clients.
    type: str
    default: ""
  username:
    description: Username for authentication (client mode).
    type: str
    default: ""
  password:
    description: Password for authentication (client mode).
    type: str
    default: ""
    no_log: true
  state:
    description: Desired state of the instance.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create an OpenVPN server instance
  by_systems.opnsense.opnsense_ovpn_instance:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Corporate VPN Server"
    role: server
    proto: UDP
    listen_port: 1194
    server: "10.8.0.0/24"
    ca: "{{ opn_ca_uuid }}"
    cert: "{{ opn_cert_uuid }}"
    state: present

- name: Remove an OpenVPN instance
  by_systems.opnsense.opnsense_ovpn_instance:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Corporate VPN Server"
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
            "enabled": {"type": "bool", "default": True},
            "role": {
                "type": "str",
                "choices": ["server", "client"],
                "default": "server",
            },
            "dev_type": {"type": "str", "default": ""},
            "proto": {"type": "str", "default": ""},
            "listen_port": {"type": "int"},
            "server": {"type": "str", "default": ""},
            "cert": {"type": "str", "default": ""},
            "ca": {"type": "str", "default": ""},
            "local": {"type": "str", "default": ""},
            "remote": {"type": "str", "default": ""},
            "keepalive_interval": {"type": "str", "default": ""},
            "keepalive_timeout": {"type": "str", "default": ""},
            "tun_mtu": {"type": "str", "default": ""},
            "maxclients": {"type": "str", "default": ""},
            "username": {"type": "str", "default": ""},
            "password": {"type": "str", "default": "", "no_log": True},
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
        "enabled": "1" if module.params["enabled"] else "0",
        "role": module.params["role"],
    }
    if module.params["dev_type"]:
        params["dev_type"] = module.params["dev_type"]
    if module.params["proto"]:
        params["proto"] = module.params["proto"]
    if module.params["listen_port"] is not None:
        params["port"] = str(module.params["listen_port"])
    if module.params["server"]:
        params["server"] = module.params["server"]
    if module.params["cert"]:
        params["cert"] = module.params["cert"]
    if module.params["ca"]:
        params["ca"] = module.params["ca"]
    if module.params["local"]:
        params["local"] = module.params["local"]
    if module.params["remote"]:
        params["remote"] = module.params["remote"]
    if module.params["keepalive_interval"]:
        params["keepalive_interval"] = module.params["keepalive_interval"]
    if module.params["keepalive_timeout"]:
        params["keepalive_timeout"] = module.params["keepalive_timeout"]
    if module.params["tun_mtu"]:
        params["tun_mtu"] = module.params["tun_mtu"]
    if module.params["maxclients"]:
        params["maxclients"] = module.params["maxclients"]
    if module.params["username"]:
        params["username"] = module.params["username"]
    if module.params["password"]:
        params["password"] = module.params["password"]

    from opnsense.managers.vpn.ovpn_instance import OvpnInstanceManager

    run_module(module, OvpnInstanceManager, params)


if __name__ == "__main__":
    main()
