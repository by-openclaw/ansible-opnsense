#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense traffic shaper queue management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ts_queue
short_description: Manage OPNsense traffic shaper queues
version_added: "0.3.0"
description:
  - Create, update, or delete traffic shaper queue entries on OPNsense.
  - Thin wrapper around lib-opnsense TsQueueManager.ensure().
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
  description:
    description: Queue description (unique identifier).
    type: str
    required: true
  weight:
    description: Queue weight (1-100).
    type: int
    default: 50
  enabled:
    description: Whether the queue is enabled.
    type: bool
    default: true
  mask:
    description: Dynamic queue mask.
    type: str
    choices: [none, src-ip, dst-ip, src-ip6, dst-ip6]
    default: none
  state:
    description: Desired state of the queue.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create a traffic shaper queue
  by_systems.opnsense.opnsense_ts_queue:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "VoIP priority queue"
    weight: 80
    state: present

- name: Remove a traffic shaper queue
  by_systems.opnsense.opnsense_ts_queue:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "VoIP priority queue"
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
            "description": {"type": "str", "required": True},
            "weight": {"type": "int", "default": 50},
            "enabled": {"type": "bool", "default": True},
            "mask": {
                "type": "str",
                "choices": ["none", "src-ip", "dst-ip", "src-ip6", "dst-ip6"],
                "default": "none",
            },
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {
        "description": module.params["description"],
        "weight": str(module.params["weight"]),
        "enabled": "1" if module.params["enabled"] else "0",
        "mask": module.params["mask"],
    }

    from opnsense.managers.shaper.ts_queue import TsQueueManager

    run_module(module, TsQueueManager, params)


if __name__ == "__main__":
    main()
