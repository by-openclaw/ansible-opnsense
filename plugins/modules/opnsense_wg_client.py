#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense Manage OPNsense WireGuard peers."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_wg_client
short_description: Manage OPNsense WireGuard peers
version_added: "0.3.0"
description:
  - Thin wrapper around lib-opnsense WgClientManager.ensure().
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
  by_systems.opnsense.opnsense_wg_client:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: "example"
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
            "name": {"type": "str", "required": True},
            "pubkey": {"type": "str", "default": ""},
            "tunneladdress": {"type": "str", "default": ""},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {"name": module.params["name"]}
    params["pubkey"] = module.params["pubkey"]
    if module.params["tunneladdress"]:
        params["tunneladdress"] = module.params["tunneladdress"]

    from opnsense.managers.wg_client import WgClientManager

    run_module(module, WgClientManager, params)


if __name__ == "__main__":
    main()
