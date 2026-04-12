#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense IPsec remote authentication management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ipsec_remote
short_description: Manage OPNsense IPsec remote authentication
version_added: "0.3.0"
description:
  - Create, update, or delete IPsec remote authentication entries on OPNsense.
  - Thin wrapper around lib-opnsense IpsecRemoteManager.ensure().
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
    description: Remote auth description (unique identifier).
    type: str
    required: true
  enabled:
    description: Whether the remote auth entry is enabled.
    type: bool
    default: true
  connection:
    description: Parent connection UUID or name.
    type: str
    default: ""
  auth:
    description: Authentication method.
    type: str
    default: ""
  id:
    description: Remote identity.
    type: str
    default: ""
  eap_id:
    description: EAP identity.
    type: str
    default: ""
  round:
    description: Authentication round.
    type: str
    default: ""
  state:
    description: Desired state of the remote auth entry.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create IPsec remote authentication
  by_systems.opnsense.opnsense_ipsec_remote:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Remote PSK auth"
    auth: psk
    id: "peer.example.com"
    state: present

- name: Remove IPsec remote authentication
  by_systems.opnsense.opnsense_ipsec_remote:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Remote PSK auth"
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
            "connection": {"type": "str", "default": ""},
            "auth": {"type": "str", "default": ""},
            "id": {"type": "str", "default": ""},
            "eap_id": {"type": "str", "default": ""},
            "round": {"type": "str", "default": ""},
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
    }
    if module.params["connection"]:
        params["connection"] = module.params["connection"]
    if module.params["auth"]:
        params["auth"] = module.params["auth"]
    if module.params["id"]:
        params["id"] = module.params["id"]
    if module.params["eap_id"]:
        params["eap_id"] = module.params["eap_id"]
    if module.params["round"]:
        params["round"] = module.params["round"]

    from opnsense.managers.vpn.ipsec_remote import IpsecRemoteManager

    run_module(module, IpsecRemoteManager, params)


if __name__ == "__main__":
    main()
