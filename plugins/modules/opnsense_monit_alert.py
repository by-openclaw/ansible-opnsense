#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_monit_alert — thin wrapper on lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_monit_alert
short_description: Manage OPNsense Monit alert recipients
version_added: "0.5.0"
description:
  - CRUD for Monit alert entries (matched by I(recipient)) — lib-opnsense MonitAlertManager.ensure().
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
  recipient:
    description: Recipient e-mail address (match key).
    type: str
    required: true
  enabled:
    description: Enable the alert.
    type: bool
  noton:
    description: Invert the event selection (alert on everything BUT I(events)).
    type: bool
  events:
    description: Comma-separated event list (empty = all).
    type: str
  format:
    description: Custom mail format (from/subject/message lines).
    type: str
  reminder:
    description: Reminder cycles.
    type: str
  description:
    description: Description.
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
- name: Manage OPNsense Monit alert recipients
  by_systems.opnsense.opnsense_monit_alert:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    recipient: alerts@example.test
    enabled: true
    format: |-
      from: monit@example.test
      subject: [$HOST] $SERVICE $EVENT
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


_BOOL_FIELDS = ("enabled", "noton")
_STR_FIELDS = ("recipient", "events", "format", "reminder", "description")
_ENUMS = {}


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update({f: {"type": "bool"} for f in _BOOL_FIELDS})
    spec.update(
        {
            f: {
                "type": "str",
                "required": f in ("recipient",),
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

    # Match key ('recipient') always; other options only when set, so an unset
    # option leaves that field untouched on an existing entry.
    params: dict = {}
    for field in _BOOL_FIELDS:
        if module.params.get(field) is not None:
            params[field] = "1" if module.params[field] else "0"
    for field in _STR_FIELDS:
        if module.params.get(field) is not None:
            params[field] = module.params[field]

    from opnsense.managers.monit.alert import MonitAlertManager

    run_module(module, MonitAlertManager, params)


if __name__ == "__main__":
    main()
