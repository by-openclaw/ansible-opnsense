#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense IPsec keypair management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ipsec_keypair
short_description: Manage OPNsense IPsec keypairs
version_added: "0.3.0"
description:
  - Create, update, or delete IPsec keypair entries on OPNsense.
  - Thin wrapper around lib-opnsense IpsecKeypairManager.ensure().
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
  name:
    description: Keypair name (unique identifier).
    type: str
    required: true
  keyType:
    description: Key type (e.g. RSA, ECDSA).
    type: str
    default: ""
  publicKey:
    description: Public key in PEM format.
    type: str
    default: ""
  privateKey:
    description: Private key in PEM format.
    type: str
    default: ""
    no_log: true
  state:
    description: Desired state of the keypair.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create an IPsec keypair
  by_systems.opnsense.opnsense_ipsec_keypair:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: "site-a-keypair"
    keyType: RSA
    publicKey: "{{ vault_ipsec_pubkey }}"
    privateKey: "{{ vault_ipsec_privkey }}"
    state: present

- name: Remove an IPsec keypair
  by_systems.opnsense.opnsense_ipsec_keypair:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: "site-a-keypair"
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
            "name": {"type": "str", "required": True},
            "keyType": {"type": "str", "default": ""},
            "publicKey": {"type": "str", "default": ""},
            "privateKey": {"type": "str", "default": "", "no_log": True},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {
        "name": module.params["name"],
    }
    if module.params["keyType"]:
        params["keyType"] = module.params["keyType"]
    if module.params["publicKey"]:
        params["publicKey"] = module.params["publicKey"]
    if module.params["privateKey"]:
        params["privateKey"] = module.params["privateKey"]

    from opnsense.managers.vpn.ipsec_keypair import IpsecKeypairManager

    run_module(module, IpsecKeypairManager, params)


if __name__ == "__main__":
    main()
