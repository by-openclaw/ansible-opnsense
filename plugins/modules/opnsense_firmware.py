#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_firmware — thin wrapper on lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_firmware
short_description: Apply pending OPNsense firmware updates/upgrades (reboots the device) and wait for the target version
version_added: "0.5.0"
description:
  - >
    Runs the firmware check job, then applies the pending point update (C(updated)) or major upgrade (C(upgraded)) ONLY when the device reports one — lib-opnsense FirmwareManager.ensure().
  - >
    The device reboots. With I(target) set, the module waits until C(product_version) contains it (connection errors during the reboot are tolerated).
  - >
    In check mode nothing is fired and C(diff.before) carries the resolved status (C(status): none|update|upgrade, C(product_version)) — use that to report what is pending.
  - Applying firmware is a deliberate per-environment window, never part of a routine converge.
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
  target:
    description: Version substring to wait for after the reboot (e.g. C(26.7.3)). Omit to return right after firing.
    type: str
  check_timeout:
    description: Seconds allowed for the check job.
    type: int
    default: 120
  wait_timeout:
    description: Seconds allowed for the device to come back on I(target).
    type: int
    default: 1500
  state:
    description: C(updated) applies a pending point update; C(upgraded) applies a pending major upgrade (or the pending update if that is what is queued).
    type: str
    choices: [updated, upgraded]
    default: updated
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Firmware window — apply the pending point update and wait for 26.7.3
  by_systems.opnsense.opnsense_firmware:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    state: updated
    target: "26.7.3"

- name: Report what is pending without touching anything
  by_systems.opnsense.opnsense_firmware:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
  check_mode: true
  register: fw
"""

RETURN = r"""
changed:
  description: Whether state on the firewall was modified.
  type: bool
  returned: always
action:
  description: One of C(updated), C(upgraded) or C(noop).
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


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update(
        {
            "target": {"type": "str"},
            "check_timeout": {"type": "int", "default": 120},
            "wait_timeout": {"type": "int", "default": 1500},
            "state": {
                "type": "str",
                "choices": ["updated", "upgraded"],
                "default": "updated",
            },
        }
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    from opnsense.managers.services.firmware import FirmwareManager

    run_module(
        module,
        FirmwareManager,
        {},
        ensure_kwargs={
            "target": module.params["target"],
            "check_timeout": module.params["check_timeout"],
            "wait_timeout": module.params["wait_timeout"],
        },
    )


if __name__ == "__main__":
    main()
