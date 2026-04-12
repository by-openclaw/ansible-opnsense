#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense VLAN interface management."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_if_vlan
short_description: Manage OPNsense VLAN interfaces
version_added: "0.2.0"
description:
  - Create, update, or delete VLAN interfaces on OPNsense.
  - Thin wrapper around lib-opnsense IfVlanManager.ensure().
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
  tag:
    description: VLAN tag ID (used as match key).
    type: int
    required: true
  if_parent:
    description: >
      Parent interface device name (used as match key).
      Maps to the "if" field in the OPNsense API.
    type: str
    required: true
  pcp:
    description: Priority Code Point (802.1p).
    type: int
    default: 0
  proto:
    description: VLAN encapsulation protocol.
    type: str
    choices: ["", "802.1q", "802.1ad"]
    default: ""
  descr:
    description: VLAN description.
    type: str
    default: ""
  state:
    description: Desired state of the VLAN.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create a VLAN interface
  by_systems.opnsense.opnsense_if_vlan:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    tag: 100
    if_parent: "vtnet0"
    descr: "Management VLAN"
    state: present

- name: Idempotent check — no changes expected
  by_systems.opnsense.opnsense_if_vlan:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    tag: 100
    if_parent: "vtnet0"
    descr: "Management VLAN"
    state: present

- name: Remove a VLAN interface
  by_systems.opnsense.opnsense_if_vlan:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    tag: 100
    if_parent: "vtnet0"
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
            "tag": {"type": "int", "required": True},
            "if_parent": {"type": "str", "required": True},
            "pcp": {"type": "int", "default": 0},
            "proto": {
                "type": "str",
                "choices": ["", "802.1q", "802.1ad"],
                "default": "",
            },
            "descr": {"type": "str", "default": ""},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {
        "tag": str(module.params["tag"]),
        "if": module.params["if_parent"],
    }
    if module.params["pcp"]:
        params["pcp"] = str(module.params["pcp"])
    if module.params["proto"]:
        params["proto"] = module.params["proto"]
    if module.params["descr"]:
        params["descr"] = module.params["descr"]

    from opnsense.managers.interfaces.vlan import IfVlanManager

    run_module(module, IfVlanManager, params)


if __name__ == "__main__":
    main()
