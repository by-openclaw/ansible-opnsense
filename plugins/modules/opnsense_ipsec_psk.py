#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense IPsec pre-shared key management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ipsec_psk
short_description: Manage OPNsense IPsec pre-shared keys
version_added: "0.3.0"
description:
  - Create, update, or delete IPsec pre-shared key entries on OPNsense.
  - Thin wrapper around lib-opnsense IpsecPskManager.ensure().
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
    description: PSK description (unique identifier).
    type: str
    required: true
  ident:
    description: Local identity.
    type: str
    default: ""
  remote_ident:
    description: Remote identity.
    type: str
    default: ""
  keyType:
    description: Key type.
    type: str
    default: ""
  Key:
    description: Pre-shared key value.
    type: str
    default: ""
    no_log: true
  state:
    description: Desired state of the PSK entry.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create an IPsec pre-shared key
  by_systems.opnsense.opnsense_ipsec_psk:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Site A PSK"
    ident: "vpn.example.com"
    remote_ident: "peer.example.com"
    keyType: PSK
    Key: "{{ vault_ipsec_psk }}"
    state: present

- name: Remove an IPsec pre-shared key
  by_systems.opnsense.opnsense_ipsec_psk:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Site A PSK"
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
            "ident": {"type": "str", "default": ""},
            "remote_ident": {"type": "str", "default": ""},
            "keyType": {"type": "str", "default": ""},
            "Key": {"type": "str", "default": "", "no_log": True},
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
    }
    if module.params["ident"]:
        params["ident"] = module.params["ident"]
    if module.params["remote_ident"]:
        params["remote_ident"] = module.params["remote_ident"]
    if module.params["keyType"]:
        params["keyType"] = module.params["keyType"]
    if module.params["Key"]:
        params["Key"] = module.params["Key"]

    from opnsense.managers.vpn.ipsec_psk import IpsecPskManager

    run_module(module, IpsecPskManager, params)


if __name__ == "__main__":
    main()
