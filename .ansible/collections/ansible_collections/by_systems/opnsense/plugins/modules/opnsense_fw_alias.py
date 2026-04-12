#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense firewall alias management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_fw_alias
short_description: Manage OPNsense firewall aliases
version_added: "0.2.0"
description:
  - Create, update, or delete firewall aliases on an OPNsense firewall.
  - Thin wrapper around lib-opnsense FwAliasManager.ensure().
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
  name:
    description: Alias name (unique identifier).
    type: str
    required: true
  type:
    description: >
      Alias type. Common values: host, network, port, url, urltable,
      geoip, networkgroup, mac, asn.
    type: str
    default: host
  content:
    description: >
      Alias content — IP addresses, networks, ports, or URLs.
      Multiple values separated by newlines.
    type: str
    default: ""
  description:
    description: Alias description.
    type: str
    default: ""
  enabled:
    description: Whether the alias is enabled.
    type: bool
    default: true
  proto:
    description: Protocol filter (IPv4, IPv6, or empty for both).
    type: str
    default: ""
  state:
    description: Desired state of the alias.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create a host alias
  by_systems.opnsense.opnsense_fw_alias:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: web_servers
    type: host
    content: "10.6.225.10\n10.6.225.11"
    description: "Web server pool"
    state: present

- name: Create a network alias
  by_systems.opnsense.opnsense_fw_alias:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: net_dmz
    type: network
    content: "10.6.225.0/24"
    description: "DMZ subnet"
    state: present

- name: Remove an alias
  by_systems.opnsense.opnsense_fw_alias:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: old_alias
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
            "type": {"type": "str", "default": "host"},
            "content": {"type": "str", "default": ""},
            "description": {"type": "str", "default": ""},
            "enabled": {"type": "bool", "default": True},
            "proto": {"type": "str", "default": ""},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {"name": module.params["name"]}
    if module.params["type"]:
        params["type"] = module.params["type"]
    if module.params["content"]:
        params["content"] = module.params["content"]
    if module.params["description"]:
        params["description"] = module.params["description"]
    if module.params["enabled"] is False:
        params["enabled"] = "0"
    else:
        params["enabled"] = "1"
    if module.params["proto"]:
        params["proto"] = module.params["proto"]

    from opnsense.managers.firewall.alias import FwAliasManager

    run_module(module, FwAliasManager, params)


if __name__ == "__main__":
    main()
