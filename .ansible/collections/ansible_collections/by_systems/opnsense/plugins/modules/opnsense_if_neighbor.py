#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense static ARP/NDP neighbor management."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_if_neighbor
short_description: Manage OPNsense static ARP/NDP neighbors
version_added: "0.2.0"
description:
  - Create, update, or delete static ARP/NDP neighbor entries on OPNsense.
  - Thin wrapper around lib-opnsense IfNeighborManager.ensure().
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
  ipaddress:
    description: IP address of the neighbor (used as match key).
    type: str
    required: true
  etheraddr:
    description: MAC address of the neighbor (used as match key).
    type: str
    required: true
  descr:
    description: Neighbor entry description.
    type: str
    default: ""
  state:
    description: Desired state of the neighbor entry.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create a static ARP entry
  by_systems.opnsense.opnsense_if_neighbor:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    ipaddress: "10.6.225.50"
    etheraddr: "00:11:22:33:44:55"
    descr: "Static entry for printer"
    state: present

- name: Idempotent check — no changes expected
  by_systems.opnsense.opnsense_if_neighbor:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    ipaddress: "10.6.225.50"
    etheraddr: "00:11:22:33:44:55"
    descr: "Static entry for printer"
    state: present

- name: Remove a static ARP entry
  by_systems.opnsense.opnsense_if_neighbor:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    ipaddress: "10.6.225.50"
    etheraddr: "00:11:22:33:44:55"
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
            "ipaddress": {"type": "str", "required": True},
            "etheraddr": {"type": "str", "required": True},
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
        "ipaddress": module.params["ipaddress"],
        "etheraddr": module.params["etheraddr"],
    }
    if module.params["descr"]:
        params["descr"] = module.params["descr"]

    from opnsense.managers.interfaces.neighbor import IfNeighborManager

    run_module(module, IfNeighborManager, params)


if __name__ == "__main__":
    main()
