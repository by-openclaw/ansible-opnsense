#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense API key management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_auth_api_key
short_description: Manage OPNsense API keys for users
version_added: "0.1.0"
description:
  - Create or delete API keys for OPNsense local users.
  - state=present creates a new key (returns key+secret once).
  - state=absent deletes all keys for the specified user.
  - Requires OPNsense >= 26.1.
  - "WARNING: API secret is only returned on creation. Store it immediately."
options:
  host:
    description: OPNsense hostname or IP address.
    type: str
    required: true
  key:
    description: OPNsense API key (for authentication).
    type: str
    required: true
    no_log: true
  secret:
    description: OPNsense API secret (for authentication).
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
  username:
    description: Username to create/delete API key for.
    type: str
    required: true
  state:
    description: >
      'present' creates a new API key.
      'absent' deletes ALL API keys for the user.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Generate API key for service account
  by_systems.opnsense.opnsense_auth_api_key:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    username: svc-automation
    state: present
  register: api_key_result
  no_log: true

- name: Store the generated key in vault
  debug:
    msg: "Key={{ api_key_result.api_key }} Secret={{ api_key_result.api_secret }}"
  no_log: true

- name: Revoke all API keys for a user
  by_systems.opnsense.opnsense_auth_api_key:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    username: svc-old-account
    state: absent
"""

RETURN = r"""
changed:
  description: Whether the module made any changes.
  type: bool
  returned: always
action:
  description: Action performed — created, deleted, or noop.
  type: str
  returned: always
api_key:
  description: Generated API key (only on create, empty otherwise).
  type: str
  returned: on create
  no_log: true
api_secret:
  description: Generated API secret (only on create, shown ONCE).
  type: str
  returned: on create
  no_log: true
"""

import asyncio

from ansible.module_utils.basic import AnsibleModule

try:
    from ansible_collections.by_systems.opnsense.plugins.module_utils.opnsense_helper import (
        _handle_opnsense_error,
        opn_argument_spec,
    )
except ImportError:
    from plugins.module_utils.opnsense_helper import (
        _handle_opnsense_error,
        opn_argument_spec,
    )


async def _run(module: AnsibleModule) -> dict:
    """Execute API key create or delete with try/except/finally."""
    from opnsense.client import OpnsenseClient
    from opnsense.managers.auth.api_key import AuthApiKeyManager

    client = None
    try:
        client = OpnsenseClient(
            host=module.params["host"],
            key=module.params["key"],
            secret=module.params["secret"],
            port=module.params["port"],
            verify_ssl=module.params["verify_ssl"],
        )
        await client.__aenter__()

        mgr = AuthApiKeyManager(client)
        username = module.params["username"]

        if module.params["state"] == "present":
            result = await mgr.create_key(
                username=username,
                check_mode=module.check_mode,
            )
            return {
                "changed": result.changed,
                "action": result.action,
                "api_key": result.after.get("key", "") if result.after else "",
                "api_secret": result.after.get("secret", "") if result.after else "",
            }
        else:
            result = await mgr.delete_all_keys(
                username=username,
                check_mode=module.check_mode,
            )
            return {
                "changed": result.changed,
                "action": result.action,
                "api_key": "",
                "api_secret": "",
            }

    except ImportError as exc:
        module.fail_json(
            msg="lib-opnsense is required. Install with: pip install opnsense",
            exception=str(exc),
        )
    except Exception as exc:
        _handle_opnsense_error(module, exc)
    finally:
        if client is not None:
            await client.close()

    return {}


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update(
        {
            "username": {"type": "str", "required": True},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    result = asyncio.run(_run(module))
    module.exit_json(**result)


if __name__ == "__main__":
    main()
