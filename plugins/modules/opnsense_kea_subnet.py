#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense Manage Kea DHCPv4 subnets."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_kea_subnet
short_description: Manage Kea DHCPv4 subnets
version_added: "0.3.0"
description:
  - Thin wrapper around lib-opnsense KeaSubnetManager.ensure().
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
  by_systems.opnsense.opnsense_kea_subnet:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    subnet: "example"
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
            "subnet": {"type": "str", "required": True},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {"subnet": module.params["subnet"]}

    from opnsense.managers.kea_subnet import KeaSubnetManager

    run_module(module, KeaSubnetManager, params)


if __name__ == "__main__":
    main()
