#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense local user management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_auth_user
short_description: Manage OPNsense local users
version_added: "0.1.0"
description:
  - Create, update, or delete local users on an OPNsense firewall.
  - Thin wrapper around lib-opnsense AuthUserManager.ensure().
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
  name:
    description: Username (unique identifier).
    type: str
    required: true
  email:
    description: User email address.
    type: str
    default: ""
  description:
    description: User description / comment.
    type: str
    default: ""
  password:
    description: User password. Only used on create or explicit update.
    type: str
    no_log: true
  group_memberships:
    description: >
      Comma-separated list of group GIDs to assign the user to.
      OPNsense 26.1 uses numeric GIDs for group membership.
    type: str
    default: ""
  disabled:
    description: Whether the user account is disabled.
    type: bool
    default: false
  state:
    description: Desired state of the user.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Ensure service account exists
  by_systems.opnsense.opnsense_auth_user:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: svc-automation
    email: automation@example.com
    description: "CI service account"
    state: present

- name: Create user in specific group
  by_systems.opnsense.opnsense_auth_user:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: admin-user
    email: admin@example.com
    password: "{{ vault_admin_password }}"
    group_memberships: "2000,2001"
    state: present

- name: Remove a user
  by_systems.opnsense.opnsense_auth_user:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: svc-old-account
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
            "email": {"type": "str", "default": ""},
            "description": {"type": "str", "default": ""},
            "password": {"type": "str", "no_log": True, "default": None},
            "group_memberships": {"type": "str", "default": ""},
            "disabled": {"type": "bool", "default": False},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {"name": module.params["name"]}
    if module.params["email"]:
        params["email"] = module.params["email"]
    if module.params["description"]:
        params["description"] = module.params["description"]
    if module.params["password"] is not None:
        params["password"] = module.params["password"]
    if module.params["group_memberships"]:
        params["group_memberships"] = module.params["group_memberships"]
    if module.params["disabled"]:
        params["disabled"] = "1"

    from opnsense.managers.auth_user import AuthUserManager

    run_module(module, AuthUserManager, params)


if __name__ == "__main__":
    main()
