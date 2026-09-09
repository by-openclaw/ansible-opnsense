#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense firewall interface group management."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_fw_group
short_description: Manage OPNsense firewall interface groups
version_added: "0.2.0"
description:
  - Create, update, or delete firewall interface groups on OPNsense.
  - Thin wrapper around lib-opnsense FwGroupManager.ensure().
  - Requires OPNsense >= 26.1.
  - This manages firewall interface groups, not authentication groups.
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
  ifname:
    description: >
      Interface group name (used as unique identifier for matching).
      Must be a valid interface group name.
    type: str
    required: true
  members:
    description: Comma-separated list of member interfaces.
    type: str
    required: true
  descr:
    description: Description of the interface group.
    type: str
    default: ""
  state:
    description: Desired state of the interface group.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create an interface group
  by_systems.opnsense.opnsense_fw_group:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    ifname: "dmz_group"
    members: "opt1,opt2"
    descr: "DMZ interface group"
    state: present

- name: Idempotent check — no changes expected
  by_systems.opnsense.opnsense_fw_group:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    ifname: "dmz_group"
    members: "opt1,opt2"
    descr: "DMZ interface group"
    state: present

- name: Remove an interface group
  by_systems.opnsense.opnsense_fw_group:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    ifname: "dmz_group"
    members: "opt1,opt2"
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
            "ifname": {"type": "str", "required": True},
            "members": {"type": "str", "required": True},
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
        "ifname": module.params["ifname"],
        "members": module.params["members"],
    }
    if module.params["descr"]:
        params["descr"] = module.params["descr"]

    from opnsense.managers.firewall.group import FwGroupManager

    run_module(module, FwGroupManager, params)


if __name__ == "__main__":
    main()
