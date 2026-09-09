#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense Unbound DNS-over-TLS management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ub_dot
short_description: Manage OPNsense Unbound DNS-over-TLS destinations
version_added: "0.3.0"
description:
  - Create, update, or delete Unbound DNS-over-TLS (DoT) destinations on OPNsense.
  - Thin wrapper around lib-opnsense UbDotManager.ensure().
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
  server:
    description: DoT server IP address (match key).
    type: str
    required: true
  dot_port:
    description: DoT server port (match key).
    type: str
    default: "853"
  type:
    description: Transport type (only DoT supported).
    type: str
    choices: [dot]
    default: dot
  verify:
    description: Certificate CN to verify against.
    type: str
    default: ""
  domain:
    description: Domain to use this DoT server for (empty for all).
    type: str
    default: ""
  enabled:
    description: Whether the DoT destination is enabled.
    type: bool
    default: true
  description:
    description: DoT destination description.
    type: str
    default: ""
  state:
    description: Desired state of the DoT destination.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 1.0.0)
"""

EXAMPLES = r"""
- name: Add Cloudflare DoT server
  by_systems.opnsense.opnsense_ub_dot:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    server: "1.1.1.1"
    dot_port: "853"
    verify: "cloudflare-dns.com"
    description: "Cloudflare DoT"
    state: present

- name: Remove a DoT server
  by_systems.opnsense.opnsense_ub_dot:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    server: "1.1.1.1"
    dot_port: "853"
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
            "server": {"type": "str", "required": True},
            "dot_port": {"type": "str", "default": "853"},
            "type": {
                "type": "str",
                "choices": ["dot"],
                "default": "dot",
            },
            "verify": {"type": "str", "default": ""},
            "domain": {"type": "str", "default": ""},
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
        "server": module.params["server"],
        "port": module.params["dot_port"],
        "type": module.params["type"],
        "enabled": "1" if module.params["enabled"] else "0",
    }
    if module.params["verify"]:
        params["verify"] = module.params["verify"]
    if module.params["domain"]:
        params["domain"] = module.params["domain"]
    if module.params["description"]:
        params["description"] = module.params["description"]

    from opnsense.managers.dns.ub_dot import UbDotManager

    run_module(module, UbDotManager, params)


if __name__ == "__main__":
    main()
