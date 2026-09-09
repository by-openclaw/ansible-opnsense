#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense Unbound ACL management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ub_acl
short_description: Manage OPNsense Unbound DNS access control lists
version_added: "0.3.0"
description:
  - Create, update, or delete Unbound DNS access control lists on OPNsense.
  - Thin wrapper around lib-opnsense UbAclManager.ensure().
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
    description: ACL name (unique identifier / match key).
    type: str
    required: true
  action:
    description: ACL action to apply.
    type: str
    choices: [allow, deny, refuse, allow_snoop, deny_non_local, refuse_non_local]
    default: allow
  networks:
    description: >
      Networks to apply the ACL to. Multiple values separated by commas.
    type: str
    default: ""
  enabled:
    description: Whether the ACL is enabled.
    type: bool
    default: true
  description:
    description: ACL description.
    type: str
    default: ""
  state:
    description: Desired state of the ACL.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 1.0.0)
"""

EXAMPLES = r"""
- name: Create an ACL allowing LAN queries
  by_systems.opnsense.opnsense_ub_acl:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: allow_lan
    action: allow
    networks: "10.6.225.0/24"
    description: "Allow LAN DNS queries"
    state: present

- name: Deny queries from guest network
  by_systems.opnsense.opnsense_ub_acl:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: deny_guest
    action: deny
    networks: "10.6.230.0/24"
    description: "Block guest DNS"
    state: present

- name: Remove an ACL
  by_systems.opnsense.opnsense_ub_acl:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: old_acl
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
            "action": {
                "type": "str",
                "choices": [
                    "allow",
                    "deny",
                    "refuse",
                    "allow_snoop",
                    "deny_non_local",
                    "refuse_non_local",
                ],
                "default": "allow",
            },
            "networks": {"type": "str", "default": ""},
            "enabled": {"type": "bool", "default": True},
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
        "name": module.params["name"],
        "action": module.params["action"],
        "enabled": "1" if module.params["enabled"] else "0",
    }
    if module.params["networks"]:
        params["networks"] = module.params["networks"]
    if module.params["description"]:
        params["description"] = module.params["description"]

    from opnsense.managers.dns.ub_acl import UbAclManager

    run_module(module, UbAclManager, params)


if __name__ == "__main__":
    main()
