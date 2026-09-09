#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense IPsec connection management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ipsec_conn
short_description: Manage OPNsense IPsec connections
version_added: "0.3.0"
description:
  - Create, update, or delete IPsec connections on OPNsense.
  - Thin wrapper around lib-opnsense IpsecConnManager.ensure().
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
    description: Connection description (unique identifier).
    type: str
    required: true
  enabled:
    description: Whether the connection is enabled.
    type: bool
    default: true
  version:
    description: IKE version (1 or 2).
    type: str
    default: ""
  aggressive:
    description: Use aggressive mode.
    type: bool
    default: false
  mobike:
    description: Enable MOBIKE.
    type: bool
    default: false
  reauth_time:
    description: Re-authentication time.
    type: str
    default: ""
  rekey_time:
    description: Rekey time.
    type: str
    default: ""
  dpd_delay:
    description: Dead peer detection delay.
    type: str
    default: ""
  dpd_timeout:
    description: Dead peer detection timeout.
    type: str
    default: ""
  keyingtries:
    description: Number of keying tries.
    type: str
    default: ""
  state:
    description: Desired state of the connection.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create an IPsec connection
  by_systems.opnsense.opnsense_ipsec_conn:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Site-to-site VPN"
    version: "2"
    dpd_delay: "30"
    state: present

- name: Remove an IPsec connection
  by_systems.opnsense.opnsense_ipsec_conn:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Site-to-site VPN"
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
            "version": {"type": "str", "default": ""},
            "aggressive": {"type": "bool", "default": False},
            "mobike": {"type": "bool", "default": False},
            "reauth_time": {"type": "str", "default": ""},
            "rekey_time": {"type": "str", "default": ""},
            "dpd_delay": {"type": "str", "default": ""},
            "dpd_timeout": {"type": "str", "default": ""},
            "keyingtries": {"type": "str", "default": ""},
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
        "aggressive": "1" if module.params["aggressive"] else "0",
        "mobike": "1" if module.params["mobike"] else "0",
    }
    if module.params["version"]:
        params["version"] = module.params["version"]
    if module.params["reauth_time"]:
        params["reauth_time"] = module.params["reauth_time"]
    if module.params["rekey_time"]:
        params["rekey_time"] = module.params["rekey_time"]
    if module.params["dpd_delay"]:
        params["dpd_delay"] = module.params["dpd_delay"]
    if module.params["dpd_timeout"]:
        params["dpd_timeout"] = module.params["dpd_timeout"]
    if module.params["keyingtries"]:
        params["keyingtries"] = module.params["keyingtries"]

    from opnsense.managers.vpn.ipsec_conn import IpsecConnManager

    run_module(module, IpsecConnManager, params)


if __name__ == "__main__":
    main()
