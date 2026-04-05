#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense Manage Kea DHCPv4 reservations."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_kea_reservation
short_description: Manage Kea DHCPv4 reservations
version_added: "0.3.0"
description:
  - Thin wrapper around lib-opnsense KeaReservationManager.ensure().
  - Requires OPNsense >= 25.1.
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
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Ensure resource
  by_systems.opnsense.opnsense_kea_reservation:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    hostname: "example"
    state: present
"""

RETURN = r"""
changed:
  description: Whether the module made any changes.
  type: bool
  returned: always
action:
  description: Action performed.
  type: str
  returned: always
uuid:
  description: UUID of the affected resource.
  type: str
  returned: when available
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
            "hostname": {"type": "str", "required": True},
            "ip_address": {"type": "str", "default": ""},
            "hw_address": {"type": "str", "default": ""},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {"hostname": module.params["hostname"]}
    params["ip_address"] = module.params["ip_address"]
    params["hw_address"] = module.params["hw_address"]

    from opnsense.managers.kea_reservation import KeaReservationManager

    run_module(module, KeaReservationManager, params)


if __name__ == "__main__":
    main()
