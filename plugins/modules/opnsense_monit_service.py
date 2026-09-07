#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_monit_service — thin wrapper on lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_monit_service
short_description: Manage OPNsense Monit monitored services (checks)
version_added: "0.5.0"
description:
  - >
    CRUD for Monit service (check) entries (matched by I(name)) — lib-opnsense MonitServiceManager.ensure().
  - I(tests) and I(depends) take comma-separated UUIDs of Monit tests / services.
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
    description: Service name (match key).
    type: str
    required: true
  enabled:
    description: Enable the check.
    type: bool
  description:
    description: Description.
    type: str
  type:
    description: Check type.
    type: str
    choices: ['process', 'file', 'fifo', 'filesystem', 'directory', 'host', 'system', 'custom', 'network']
  pidfile:
    description: PID file (process).
    type: str
  match:
    description: Process match pattern.
    type: str
  path:
    description: Path (file/filesystem/directory).
    type: str
  timeout:
    description: Timeout (s).
    type: str
  starttimeout:
    description: Start timeout (s).
    type: str
  address:
    description: Address (host/network).
    type: str
  interface:
    description: Interface (network).
    type: str
  tests:
    description: Comma-separated test UUIDs.
    type: str
  depends:
    description: Comma-separated service UUIDs.
    type: str
  start:
    description: Start command.
    type: str
  stop:
    description: Stop command.
    type: str
  polltime:
    description: Poll time.
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
- name: Manage OPNsense Monit monitored services (checks)
  by_systems.opnsense.opnsense_monit_service:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: unbound
    type: process
    pidfile: /var/run/unbound.pid
    enabled: true
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


_BOOL_FIELDS = ("enabled",)
_STR_FIELDS = (
    "name",
    "description",
    "type",
    "pidfile",
    "match",
    "path",
    "timeout",
    "starttimeout",
    "address",
    "interface",
    "tests",
    "depends",
    "start",
    "stop",
    "polltime",
)
_ENUMS = {
    "type": [
        "process",
        "file",
        "fifo",
        "filesystem",
        "directory",
        "host",
        "system",
        "custom",
        "network",
    ]
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

    from opnsense.managers.monit.service import MonitServiceManager

    run_module(module, MonitServiceManager, params)


if __name__ == "__main__":
    main()
