#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense IPsec child SA management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ipsec_child
short_description: Manage OPNsense IPsec child SAs
version_added: "0.3.0"
description:
  - Create, update, or delete IPsec child SA entries on OPNsense.
  - Thin wrapper around lib-opnsense IpsecChildManager.ensure().
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
    description: Child SA description (unique identifier).
    type: str
    required: true
  enabled:
    description: Whether the child SA is enabled.
    type: bool
    default: true
  connection:
    description: Parent connection UUID or name.
    type: str
    default: ""
  mode:
    description: IPsec mode (tunnel, transport).
    type: str
    default: ""
  policies:
    description: Install policies.
    type: bool
    default: true
  rekey_time:
    description: Rekey time.
    type: str
    default: ""
  sha256_96:
    description: Enable SHA-256 96-bit truncation compatibility.
    type: bool
    default: false
  state:
    description: Desired state of the child SA.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create an IPsec child SA
  by_systems.opnsense.opnsense_ipsec_child:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "LAN-to-LAN tunnel"
    mode: tunnel
    state: present

- name: Remove an IPsec child SA
  by_systems.opnsense.opnsense_ipsec_child:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "LAN-to-LAN tunnel"
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
            "mode": {"type": "str", "default": ""},
            "policies": {"type": "bool", "default": True},
            "rekey_time": {"type": "str", "default": ""},
            "sha256_96": {"type": "bool", "default": False},
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
        "policies": "1" if module.params["policies"] else "0",
        "sha256_96": "1" if module.params["sha256_96"] else "0",
    }
    if module.params["connection"]:
        params["connection"] = module.params["connection"]
    if module.params["mode"]:
        params["mode"] = module.params["mode"]
    if module.params["rekey_time"]:
        params["rekey_time"] = module.params["rekey_time"]

    from opnsense.managers.vpn.ipsec_child import IpsecChildManager

    run_module(module, IpsecChildManager, params)


if __name__ == "__main__":
    main()
