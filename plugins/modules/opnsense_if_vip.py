#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense virtual IP (VIP) management."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_if_vip
short_description: Manage OPNsense virtual IP addresses
version_added: "0.2.0"
description:
  - Create, update, or delete virtual IP addresses on OPNsense.
  - Supports IP Alias, CARP, Proxy ARP, and Other types.
  - Thin wrapper around lib-opnsense IfVipManager.ensure().
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
  address:
    description: Virtual IP address (used as match key).
    type: str
    required: true
  interface:
    description: Interface to assign the VIP to (used as match key).
    type: str
    required: true
  mode:
    description: VIP type (used as match key).
    type: str
    required: true
    choices: [ipalias, carp, proxyarp]
  network:
    description: >
      Network mask in CIDR notation (e.g. "32" for a single host,
      "24" for a /24 subnet).
    type: str
    default: ""
  descr:
    description: VIP description.
    type: str
    default: ""
  password:
    description: CARP password (only used for mode=carp).
    type: str
    default: ""
    no_log: true
  advbase:
    description: CARP advertisement base interval in seconds.
    type: int
  advskew:
    description: CARP advertisement skew.
    type: int
  vhid:
    description: CARP Virtual Host ID.
    type: str
    default: ""
  state:
    description: Desired state of the VIP.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create an IP alias VIP
  by_systems.opnsense.opnsense_if_vip:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    address: "10.6.225.100"
    interface: lan
    mode: ipalias
    network: "32"
    descr: "Service VIP"
    state: present

- name: Idempotent check — no changes expected
  by_systems.opnsense.opnsense_if_vip:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    address: "10.6.225.100"
    interface: lan
    mode: ipalias
    network: "32"
    descr: "Service VIP"
    state: present

- name: Remove a VIP
  by_systems.opnsense.opnsense_if_vip:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    address: "10.6.225.100"
    interface: lan
    mode: ipalias
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
            "address": {"type": "str", "required": True},
            "interface": {"type": "str", "required": True},
            "mode": {
                "type": "str",
                "required": True,
                "choices": ["ipalias", "carp", "proxyarp"],
            },
            "network": {"type": "str", "default": ""},
            "descr": {"type": "str", "default": ""},
            "password": {"type": "str", "default": "", "no_log": True},
            "advbase": {"type": "int"},
            "advskew": {"type": "int"},
            "vhid": {"type": "str", "default": ""},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {
        "address": module.params["address"],
        "interface": module.params["interface"],
        "mode": module.params["mode"],
    }
    if module.params["network"]:
        params["network"] = module.params["network"]
    if module.params["descr"]:
        params["descr"] = module.params["descr"]
    if module.params["password"]:
        params["password"] = module.params["password"]
    if module.params["advbase"] is not None:
        params["advbase"] = str(module.params["advbase"])
    if module.params["advskew"] is not None:
        params["advskew"] = str(module.params["advskew"])
    if module.params["vhid"]:
        params["vhid"] = module.params["vhid"]

    from opnsense.managers.interfaces.vip import IfVipManager

    run_module(module, IfVipManager, params)


if __name__ == "__main__":
    main()
