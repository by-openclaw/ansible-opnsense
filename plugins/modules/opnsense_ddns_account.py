#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense Dynamic DNS account management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ddns_account
short_description: Manage OPNsense Dynamic DNS accounts
version_added: "0.3.0"
description:
  - Create, update, or delete Dynamic DNS (DDNS) accounts on OPNsense.
  - Thin wrapper around lib-opnsense DdnsAccountManager.ensure().
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
    description: DDNS account description (unique identifier / match key).
    type: str
    required: true
  enabled:
    description: Whether the DDNS account is enabled.
    type: bool
    default: true
  service:
    description: DDNS service provider (e.g. cloudflare, dyndns, noip).
    type: str
    default: ""
  protocol:
    description: DDNS update protocol.
    type: str
    default: ""
  server:
    description: DDNS update server address.
    type: str
    default: ""
  username:
    description: DDNS account username.
    type: str
    default: ""
  password:
    description: DDNS account password.
    type: str
    default: ""
    no_log: true
  hostnames:
    description: Hostnames to update (comma-separated).
    type: str
    required: true
  checkip:
    description: Method to check external IP.
    type: str
    required: true
  interface:
    description: Interface to use for IP detection.
    type: str
    default: ""
  state:
    description: Desired state of the DDNS account.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 1.0.0)
"""

EXAMPLES = r"""
- name: Create a Cloudflare DDNS account
  by_systems.opnsense.opnsense_ddns_account:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Cloudflare DDNS"
    service: cloudflare
    username: "{{ ddns_user }}"
    password: "{{ ddns_token }}"
    hostnames: "home.example.com"
    checkip: "web_dyndns"
    state: present

- name: Remove a DDNS account
  by_systems.opnsense.opnsense_ddns_account:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Old DDNS"
    hostnames: "old.example.com"
    checkip: "web_dyndns"
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
            "service": {"type": "str", "default": ""},
            "protocol": {"type": "str", "default": ""},
            "server": {"type": "str", "default": ""},
            "username": {"type": "str", "default": ""},
            "password": {"type": "str", "default": "", "no_log": True},
            "hostnames": {"type": "str", "required": True},
            "checkip": {"type": "str", "required": True},
            "interface": {"type": "str", "default": ""},
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
        "hostnames": module.params["hostnames"],
        "checkip": module.params["checkip"],
    }
    if module.params["service"]:
        params["service"] = module.params["service"]
    if module.params["protocol"]:
        params["protocol"] = module.params["protocol"]
    if module.params["server"]:
        params["server"] = module.params["server"]
    if module.params["username"]:
        params["username"] = module.params["username"]
    if module.params["password"]:
        params["password"] = module.params["password"]
    if module.params["interface"]:
        params["interface"] = module.params["interface"]

    from opnsense.managers.services.ddns_account import DdnsAccountManager

    run_module(module, DdnsAccountManager, params)


if __name__ == "__main__":
    main()
