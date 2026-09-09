#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense Kea DHCPv6 subnet management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_kea6_subnet
short_description: Manage OPNsense Kea DHCPv6 subnets
version_added: "0.3.0"
description:
  - Create, update, or delete Kea DHCPv6 subnets on OPNsense.
  - Thin wrapper around lib-opnsense Kea6SubnetManager.ensure().
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
  subnet:
    description: >
      IPv6 subnet in CIDR notation (e.g. fd00:225::/64). Match key.
    type: str
    required: true
  interface:
    description: Interface to bind this subnet to.
    type: str
    required: true
  description:
    description: Subnet description.
    type: str
    default: ""
  state:
    description: Desired state of the subnet.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 1.0.0)
"""

EXAMPLES = r"""
- name: Create a DHCPv6 subnet
  by_systems.opnsense.opnsense_kea6_subnet:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    subnet: "fd00:225::/64"
    interface: lan
    description: "LAN IPv6 DHCP"
    state: present

- name: Remove a DHCPv6 subnet
  by_systems.opnsense.opnsense_kea6_subnet:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    subnet: "fd00:225::/64"
    interface: lan
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
            "subnet": {"type": "str", "required": True},
            "interface": {"type": "str", "required": True},
            "description": {"type": "str", "default": ""},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {
        "subnet": module.params["subnet"],
        "interface": module.params["interface"],
    }
    if module.params["description"]:
        params["description"] = module.params["description"]

    from opnsense.managers.dhcp.kea6_subnet import Kea6SubnetManager

    run_module(module, Kea6SubnetManager, params)


if __name__ == "__main__":
    main()
