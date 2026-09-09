#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense traffic shaper pipe management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ts_pipe
short_description: Manage OPNsense traffic shaper pipes
version_added: "0.3.0"
description:
  - Create, update, or delete traffic shaper pipe entries on OPNsense.
  - Thin wrapper around lib-opnsense TsPipeManager.ensure().
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
  description:
    description: Pipe description (part of composite match key).
    type: str
    required: true
  bandwidth:
    description: Bandwidth value (part of composite match key).
    type: int
    required: true
  bandwidthMetric:
    description: Bandwidth unit (part of composite match key).
    type: str
    choices: [bit, Kbit, Mbit, Gbit]
    default: Mbit
  enabled:
    description: Whether the pipe is enabled.
    type: bool
    default: true
  delay:
    description: Delay in milliseconds.
    type: str
    default: ""
  mask:
    description: Dynamic pipe mask.
    type: str
    choices: [none, src-ip, dst-ip, src-ip6, dst-ip6]
    default: none
  scheduler:
    description: Scheduler type.
    type: str
    default: ""
  state:
    description: Desired state of the pipe.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create a 100 Mbit pipe
  by_systems.opnsense.opnsense_ts_pipe:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "WAN download limit"
    bandwidth: 100
    bandwidthMetric: Mbit
    state: present

- name: Remove a pipe
  by_systems.opnsense.opnsense_ts_pipe:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "WAN download limit"
    bandwidth: 100
    bandwidthMetric: Mbit
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
            "bandwidth": {"type": "int", "required": True},
            "bandwidthMetric": {
                "type": "str",
                "choices": ["bit", "Kbit", "Mbit", "Gbit"],
                "default": "Mbit",
            },
            "enabled": {"type": "bool", "default": True},
            "delay": {"type": "str", "default": ""},
            "mask": {
                "type": "str",
                "choices": ["none", "src-ip", "dst-ip", "src-ip6", "dst-ip6"],
                "default": "none",
            },
            "scheduler": {"type": "str", "default": ""},
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
        "bandwidth": str(module.params["bandwidth"]),
        "bandwidthMetric": module.params["bandwidthMetric"],
        "enabled": "1" if module.params["enabled"] else "0",
        "mask": module.params["mask"],
    }
    if module.params["delay"]:
        params["delay"] = module.params["delay"]
    if module.params["scheduler"]:
        params["scheduler"] = module.params["scheduler"]

    from opnsense.managers.shaper.ts_pipe import TsPipeManager

    run_module(module, TsPipeManager, params)


if __name__ == "__main__":
    main()
