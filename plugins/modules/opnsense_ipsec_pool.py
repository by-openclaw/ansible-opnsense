#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense IPsec pool management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ipsec_pool
short_description: Manage OPNsense IPsec address pools
version_added: "0.3.0"
description:
  - Create, update, or delete IPsec address pool entries on OPNsense.
  - Thin wrapper around lib-opnsense IpsecPoolManager.ensure().
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
  name:
    description: Pool name (unique identifier).
    type: str
    required: true
  enabled:
    description: Whether the pool is enabled.
    type: bool
    default: true
  addrs:
    description: Address range for the pool (CIDR notation).
    type: str
    default: ""
  dns:
    description: DNS server pushed to clients.
    type: str
    default: ""
  state:
    description: Desired state of the pool.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create an IPsec address pool
  by_systems.opnsense.opnsense_ipsec_pool:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: "vpn-pool"
    addrs: "10.10.100.0/24"
    dns: "10.10.100.1"
    state: present

- name: Remove an IPsec address pool
  by_systems.opnsense.opnsense_ipsec_pool:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: "vpn-pool"
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
            "addrs": {"type": "str", "default": ""},
            "dns": {"type": "str", "default": ""},
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
    }
    if module.params["addrs"]:
        params["addrs"] = module.params["addrs"]
    if module.params["dns"]:
        params["dns"] = module.params["dns"]

    from opnsense.managers.vpn.ipsec_pool import IpsecPoolManager

    run_module(module, IpsecPoolManager, params)


if __name__ == "__main__":
    main()
