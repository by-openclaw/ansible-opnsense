#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense IPsec VTI management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ipsec_vti
short_description: Manage OPNsense IPsec VTI interfaces
version_added: "0.3.0"
description:
  - Create, update, or delete IPsec VTI (Virtual Tunnel Interface) entries on OPNsense.
  - Thin wrapper around lib-opnsense IpsecVtiManager.ensure().
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
    description: VTI description (unique identifier).
    type: str
    required: true
  enabled:
    description: Whether the VTI is enabled.
    type: bool
    default: true
  reqid:
    description: Request ID for the VTI.
    type: str
    default: ""
  local:
    description: Local endpoint address.
    type: str
    default: ""
  remote:
    description: Remote endpoint address.
    type: str
    default: ""
  tunnel_local:
    description: Local tunnel address (inner).
    type: str
    default: ""
  tunnel_remote:
    description: Remote tunnel address (inner).
    type: str
    default: ""
  state:
    description: Desired state of the VTI.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create an IPsec VTI
  by_systems.opnsense.opnsense_ipsec_vti:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "VTI to Site B"
    reqid: "100"
    local: "203.0.113.1"
    remote: "203.0.113.2"
    tunnel_local: "10.255.0.1/30"
    tunnel_remote: "10.255.0.2/30"
    state: present

- name: Remove an IPsec VTI
  by_systems.opnsense.opnsense_ipsec_vti:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "VTI to Site B"
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
            "reqid": {"type": "str", "default": ""},
            "local": {"type": "str", "default": ""},
            "remote": {"type": "str", "default": ""},
            "tunnel_local": {"type": "str", "default": ""},
            "tunnel_remote": {"type": "str", "default": ""},
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
    if module.params["reqid"]:
        params["reqid"] = module.params["reqid"]
    if module.params["local"]:
        params["local"] = module.params["local"]
    if module.params["remote"]:
        params["remote"] = module.params["remote"]
    if module.params["tunnel_local"]:
        params["tunnel_local"] = module.params["tunnel_local"]
    if module.params["tunnel_remote"]:
        params["tunnel_remote"] = module.params["tunnel_remote"]

    from opnsense.managers.vpn.ipsec_vti import IpsecVtiManager

    run_module(module, IpsecVtiManager, params)


if __name__ == "__main__":
    main()
