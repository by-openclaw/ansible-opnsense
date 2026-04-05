# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, BY-SYSTEMS SRL
# MIT License (see LICENSE)

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
  - All API logic lives in the lib-opnsense Python library.
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
    description: User description.
    type: str
    default: ""
  password:
    description: User password. Only used on create or explicit update.
    type: str
    no_log: true
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
  - opnsense (lib-opnsense Python library)
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

- name: Remove a user
  by_systems.opnsense.opnsense_auth_user:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: svc-old-account
    state: absent

- name: Create user with password (check mode)
  by_systems.opnsense.opnsense_auth_user:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: admin-user
    email: admin@example.com
    password: "{{ vault_admin_password }}"
    state: present
  check_mode: true
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

import asyncio

from ansible.module_utils.basic import AnsibleModule


async def _run_ensure(module: AnsibleModule) -> dict:
    """Execute the ensure() call against OPNsense."""
    from opnsense.client import OpnsenseClient
    from opnsense.managers.auth_user import AuthUserManager

    params: dict = {}
    params["name"] = module.params["name"]
    if module.params["email"]:
        params["email"] = module.params["email"]
    if module.params["description"]:
        params["description"] = module.params["description"]
    if module.params["password"] is not None:
        params["password"] = module.params["password"]
    if module.params["disabled"]:
        params["disabled"] = "1"

    async with OpnsenseClient(
        host=module.params["host"],
        key=module.params["key"],
        secret=module.params["secret"],
        port=module.params["port"],
        verify_ssl=module.params["verify_ssl"],
    ) as client:
        mgr = AuthUserManager(client)
        result = await mgr.ensure(
            state=module.params["state"],
            params=params,
            check_mode=module.check_mode,
        )

    diff = {}
    if result.before is not None:
        diff["before"] = result.before
    if result.after is not None:
        diff["after"] = result.after

    return {
        "changed": result.changed,
        "action": result.action,
        "uuid": result.uuid or "",
        "diff": diff,
    }


def main() -> None:
    """Entry point for the Ansible module."""
    module = AnsibleModule(
        argument_spec={
            "host": {"type": "str", "required": True},
            "key": {"type": "str", "required": True, "no_log": True},
            "secret": {"type": "str", "required": True, "no_log": True},
            "port": {"type": "int", "default": 443},
            "verify_ssl": {"type": "bool", "default": False},
            "name": {"type": "str", "required": True},
            "email": {"type": "str", "default": ""},
            "description": {"type": "str", "default": ""},
            "password": {"type": "str", "no_log": True, "default": None},
            "disabled": {"type": "bool", "default": False},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        },
        supports_check_mode=True,
    )

    try:
        result = asyncio.run(_run_ensure(module))
    except ImportError as exc:
        module.fail_json(
            msg=(
                "lib-opnsense is required but not installed. "
                "Install with: pip install opnsense"
            ),
            exception=str(exc),
        )
    except Exception as exc:
        module.fail_json(msg=str(exc), exception=str(exc))

    module.exit_json(**result)


if __name__ == "__main__":
    main()
