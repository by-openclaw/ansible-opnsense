#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_monit_test — thin wrapper on lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_monit_test
short_description: Manage OPNsense Monit tests (conditions)
version_added: "0.5.0"
description:
  - CRUD for Monit test entries (matched by I(name)) — lib-opnsense MonitTestManager.ensure().
  - >
    OPNsense silently coerces I(type) to C(Custom) when I(condition) is not one of that type's fixed
    expressions (e.g. C(Existence) expects C(not exist)); a free-form condition such as
    C(does not exist) belongs to C(Custom), otherwise the second run reports a change.
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
    description: Test name (match key).
    type: str
    required: true
  type:
    description: Test type.
    type: str
    choices: ['Existence', 'SystemResource', 'ProcessResource', 'ProcessDiskIO', 'FileChecksum', 'Timestamp', 'FileSize', 'FileContent', 'FilesystemMountFlags', 'SpaceUsage', 'InodeUsage', 'DiskIO', 'Permisssion', 'UID', 'GID', 'PID', 'PPID', 'Uptime', 'ProgramStatus', 'NetworkInterface', 'NetworkPing', 'Connection', 'Custom']
  condition:
    description: Monit condition expression (e.g. C(does not exist)).
    type: str
  action:
    description: Action when the condition holds.
    type: str
    choices: ['alert', 'restart', 'start', 'stop', 'exec', 'unmonitor']
  path:
    description: Path for exec actions.
    type: str
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Manage OPNsense Monit tests (conditions)
  by_systems.opnsense.opnsense_monit_test:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: ProcessDown
    type: Existence
    condition: does not exist
    action: alert
"""

RETURN = r"""
changed:
  description: Whether state on the firewall was modified.
  type: bool
  returned: always
action:
  description: One of C(created), C(updated), C(deleted) or C(noop).
  type: str
  returned: always
diff:
  description: Before/after state.
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


_BOOL_FIELDS = ()
_STR_FIELDS = ("name", "type", "condition", "action", "path")
_ENUMS = {
    "type": [
        "Existence",
        "SystemResource",
        "ProcessResource",
        "ProcessDiskIO",
        "FileChecksum",
        "Timestamp",
        "FileSize",
        "FileContent",
        "FilesystemMountFlags",
        "SpaceUsage",
        "InodeUsage",
        "DiskIO",
        "Permisssion",
        "UID",
        "GID",
        "PID",
        "PPID",
        "Uptime",
        "ProgramStatus",
        "NetworkInterface",
        "NetworkPing",
        "Connection",
        "Custom",
    ],
    "action": ["alert", "restart", "start", "stop", "exec", "unmonitor"],
}


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update({f: {"type": "bool"} for f in _BOOL_FIELDS})
    spec.update(
        {
            f: {
                "type": "str",
                "required": f in ("name",),
                **({"choices": _ENUMS[f]} if f in _ENUMS else {}),
            }
            for f in _STR_FIELDS
        }
    )
    spec.update(
        {
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            }
        }
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    # Match key ('name') always; other options only when set, so an unset
    # option leaves that field untouched on an existing entry.
    params: dict = {}
    for field in _BOOL_FIELDS:
        if module.params.get(field) is not None:
            params[field] = "1" if module.params[field] else "0"
    for field in _STR_FIELDS:
        if module.params.get(field) is not None:
            params[field] = module.params[field]

    from opnsense.managers.monit.test import MonitTestManager

    run_module(module, MonitTestManager, params)


if __name__ == "__main__":
    main()
