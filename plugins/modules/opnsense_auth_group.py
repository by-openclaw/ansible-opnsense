#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, BY-SYSTEMS <engineering@by-systems.be>
# MIT License (see LICENSE)

"""Ansible module for OPNsense local group management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_auth_group
short_description: Manage OPNsense local groups
version_added: "0.1.0"
description:
  - Create, update, or delete local groups on an OPNsense firewall.
  - Thin wrapper around lib-opnsense AuthGroupManager.ensure().
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
    description: Group name (unique identifier).
    type: str
    required: true
  description:
    description: Group description.
    type: str
    default: ""
  state:
    description: Desired state of the group.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense Python library)
"""

EXAMPLES = r"""
- name: Ensure automation group exists
  by_systems.opnsense.opnsense_auth_group:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: grp-automation
    description: "Automation service accounts"
    state: present

- name: Remove a group
  by_systems.opnsense.opnsense_auth_group:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: grp-deprecated
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

import asyncio

from ansible.module_utils.basic import AnsibleModule


async def _run_ensure(module: AnsibleModule) -> dict:
    """Execute the ensure() call against OPNsense."""
    from opnsense.client import OpnsenseClient
    from opnsense.managers.auth_group import AuthGroupManager

    params: dict = {}
    params["name"] = module.params["name"]
    if module.params["description"]:
        params["description"] = module.params["description"]

    async with OpnsenseClient(
        host=module.params["host"],
        key=module.params["key"],
        secret=module.params["secret"],
        port=module.params["port"],
        verify_ssl=module.params["verify_ssl"],
    ) as client:
        mgr = AuthGroupManager(client)
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
            "description": {"type": "str", "default": ""},
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
