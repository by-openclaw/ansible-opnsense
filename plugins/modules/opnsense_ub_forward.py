#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense Unbound DNS forward management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ub_forward
short_description: Manage OPNsense Unbound DNS forwarding domains
version_added: "0.3.0"
description:
  - Create, update, or delete Unbound DNS forwarding entries on OPNsense.
  - Thin wrapper around lib-opnsense UbForwardManager.ensure().
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
  domain:
    description: Domain to forward queries for (match key).
    type: str
    required: true
  server:
    description: DNS server IP address to forward to (match key).
    type: str
    default: ""
  type:
    description: Forward type — forward or stub.
    type: str
    choices: [forward, stub]
    default: forward
  forward_port:
    description: DNS server port to forward to.
    type: str
    default: ""
  enabled:
    description: Whether the forwarding entry is enabled.
    type: bool
    default: true
  description:
    description: Forwarding entry description.
    type: str
    default: ""
  state:
    description: Desired state of the forwarding entry.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 1.0.0)
"""

EXAMPLES = r"""
- name: Forward internal domain to local DNS
  by_systems.opnsense.opnsense_ub_forward:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    domain: internal.example.com
    server: "10.6.225.1"
    type: forward
    description: "Internal domain forwarding"
    state: present

- name: Remove a forwarding entry
  by_systems.opnsense.opnsense_ub_forward:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    domain: old.example.com
    server: "10.6.225.1"
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
            "domain": {"type": "str", "required": True},
            "server": {"type": "str", "default": ""},
            "type": {
                "type": "str",
                "choices": ["forward", "stub"],
                "default": "forward",
            },
            "forward_port": {"type": "str", "default": ""},
            "enabled": {"type": "bool", "default": True},
            "description": {"type": "str", "default": ""},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {
        "domain": module.params["domain"],
        "server": module.params["server"],
        "type": module.params["type"],
        "enabled": "1" if module.params["enabled"] else "0",
    }
    if module.params["forward_port"]:
        params["port"] = module.params["forward_port"]
    if module.params["description"]:
        params["description"] = module.params["description"]

    from opnsense.managers.dns.ub_forward import UbForwardManager

    run_module(module, UbForwardManager, params)


if __name__ == "__main__":
    main()
