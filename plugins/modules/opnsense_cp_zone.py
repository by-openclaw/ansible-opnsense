#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense Captive Portal zone management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_cp_zone
short_description: Manage OPNsense Captive Portal zones
version_added: "0.3.0"
description:
  - Create, update, or delete Captive Portal zones on OPNsense.
  - Thin wrapper around lib-opnsense CpZoneManager.ensure().
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
    description: Zone description (unique identifier / match key).
    type: str
    required: true
  enabled:
    description: Whether the zone is enabled.
    type: bool
    default: true
  interfaces:
    description: >
      Interfaces bound to this zone. Comma-separated list.
    type: str
    default: ""
  authservers:
    description: >
      Authentication servers for this zone. Comma-separated list.
    type: str
    default: ""
  idletimeout:
    description: Idle timeout in minutes (0 for no timeout).
    type: int
    default: 0
  hardtimeout:
    description: Hard timeout in minutes (0 for no timeout).
    type: int
    default: 0
  concurrentlogins:
    description: Allow concurrent logins for the same user.
    type: bool
    default: true
  certificate:
    description: TLS certificate UUID for the portal.
    type: str
    default: ""
  servername:
    description: Server hostname for the portal redirect.
    type: str
    default: ""
  state:
    description: Desired state of the zone.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 1.0.0)
"""

EXAMPLES = r"""
- name: Create a captive portal zone
  by_systems.opnsense.opnsense_cp_zone:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Guest WiFi Portal"
    interfaces: "opt1"
    idletimeout: 30
    hardtimeout: 480
    state: present

- name: Remove a captive portal zone
  by_systems.opnsense.opnsense_cp_zone:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Guest WiFi Portal"
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
            "enabled": {"type": "bool", "default": True},
            "interfaces": {"type": "str", "default": ""},
            "authservers": {"type": "str", "default": ""},
            "idletimeout": {"type": "int", "default": 0},
            "hardtimeout": {"type": "int", "default": 0},
            "concurrentlogins": {"type": "bool", "default": True},
            "certificate": {"type": "str", "default": ""},
            "servername": {"type": "str", "default": ""},
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
        "enabled": "1" if module.params["enabled"] else "0",
        "concurrentlogins": "1" if module.params["concurrentlogins"] else "0",
    }
    if module.params["interfaces"]:
        params["interfaces"] = module.params["interfaces"]
    if module.params["authservers"]:
        params["authservers"] = module.params["authservers"]
    if module.params["idletimeout"]:
        params["idletimeout"] = str(module.params["idletimeout"])
    if module.params["hardtimeout"]:
        params["hardtimeout"] = str(module.params["hardtimeout"])
    if module.params["certificate"]:
        params["certificate"] = module.params["certificate"]
    if module.params["servername"]:
        params["servername"] = module.params["servername"]

    from opnsense.managers.services.cp_zone import CpZoneManager

    run_module(module, CpZoneManager, params)


if __name__ == "__main__":
    main()
