#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense LAGG (link aggregation) interface management."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_if_lagg
short_description: Manage OPNsense LAGG interfaces
version_added: "0.2.0"
description:
  - Create, update, or delete LAGG (link aggregation) interfaces on OPNsense.
  - Thin wrapper around lib-opnsense IfLaggManager.ensure().
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
  descr:
    description: LAGG description (used as unique identifier for matching).
    type: str
    required: true
  proto:
    description: LAGG aggregation protocol.
    type: str
    choices: [none, lacp, failover, fec, loadbalance]
    default: lacp
  state:
    description: Desired state of the LAGG.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create a LAGG interface with LACP
  by_systems.opnsense.opnsense_if_lagg:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    descr: "Uplink bond"
    proto: lacp
    state: present

- name: Idempotent check — no changes expected
  by_systems.opnsense.opnsense_if_lagg:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    descr: "Uplink bond"
    proto: lacp
    state: present

- name: Remove a LAGG interface
  by_systems.opnsense.opnsense_if_lagg:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    descr: "Uplink bond"
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
            "descr": {"type": "str", "required": True},
            "proto": {
                "type": "str",
                "choices": ["none", "lacp", "failover", "fec", "loadbalance"],
                "default": "lacp",
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
        "descr": module.params["descr"],
        "proto": module.params["proto"],
    }

    from opnsense.managers.interfaces.lagg import IfLaggManager

    run_module(module, IfLaggManager, params)


if __name__ == "__main__":
    main()
