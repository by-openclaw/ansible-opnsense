#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense privilege assignment via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_auth_priv
short_description: Assign or unassign OPNsense privileges
version_added: "0.1.0"
description:
  - Assign or unassign a privilege to/from a user or group.
  - Thin wrapper around lib-opnsense AuthPrivManager.ensure().
  - Requires OPNsense >= 26.1 (UUID-based privilege assignment).
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
  priv_id:
    description: >
      Privilege identifier (e.g. 'page-all', 'page-diagnostics-arptable').
      See OPNsense WebGUI System > Access > Privileges for available IDs.
    type: str
    required: true
  target_type:
    description: Whether to assign to a user or group.
    type: str
    choices: [user, group]
    required: true
  target_name:
    description: Name of the user or group to assign/unassign the privilege.
    type: str
    required: true
  state:
    description: >
      'present' assigns the privilege, 'absent' unassigns it.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Grant full admin to admins group
  by_systems.opnsense.opnsense_auth_priv:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    priv_id: page-all
    target_type: group
    target_name: admins
    state: present

- name: Grant diagnostics access to monitoring user
  by_systems.opnsense.opnsense_auth_priv:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    priv_id: page-diagnostics-arptable
    target_type: user
    target_name: svc-monitoring
    state: present

- name: Revoke privilege from group
  by_systems.opnsense.opnsense_auth_priv:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    priv_id: page-status-interfaces
    target_type: group
    target_name: grp-deprecated
    state: absent
"""

RETURN = r"""
changed:
  description: Whether the module made any changes.
  type: bool
  returned: always
action:
  description: Action performed — created (assigned), deleted (unassigned), or noop.
  type: str
  returned: always
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
    """Execute the privilege ensure() call with try/except/finally."""
    from opnsense.client import OpnsenseClient
    from opnsense.managers.auth.priv import AuthPrivManager

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

        mgr = AuthPrivManager(client)
        result = await mgr.ensure(
            priv_id=module.params["priv_id"],
            target_type=module.params["target_type"],
            target_name=module.params["target_name"],
            state=module.params["state"],
            check_mode=module.check_mode,
        )

        return {
            "changed": result.changed,
            "action": result.action,
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
            "priv_id": {"type": "str", "required": True},
            "target_type": {
                "type": "str",
                "choices": ["user", "group"],
                "required": True,
            },
            "target_name": {"type": "str", "required": True},
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
