#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_acme_account — thin wrapper on lib-opnsense (AcmeAccountManager)."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_acme_account
short_description: Manage OPNsense ACME (os-acme-client) CA accounts
version_added: "0.6.0"
description:
  - CRUD for ACME accounts (matched by I(name)) — lib-opnsense AcmeAccountManager.ensure().
  - >
    C(state=registered) = present + register the account with its CA when its last status
    is not C(200) (idempotent: a registered account is a noop).
  - Requires the C(os-acme-client) plugin.
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
    description: Account name (match key).
    type: str
    required: true
  description:
    description: Free-text description.
    type: str
  email:
    description: Contact e-mail registered with the CA.
    type: str
  ca:
    description: CA directory.
    type: str
    choices: [letsencrypt, letsencrypt_test, buypass, buypass_test, google, google_test, sslcom, zerossl, custom]
  custom_ca:
    description: Custom ACME directory URL (when I(ca=custom)).
    type: str
  eab_kid:
    description: External Account Binding key id.
    type: str
    no_log: true
  eab_hmac:
    description: External Account Binding HMAC key.
    type: str
    no_log: true
  enabled:
    description: Enable the account.
    type: bool
  state:
    description: Desired state.
    type: str
    choices: [present, absent, registered]
    default: present
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Let's Encrypt account, registered with the CA
  by_systems.opnsense.opnsense_acme_account:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: letsencrypt
    email: ops@example.com
    ca: letsencrypt
    state: registered
"""

RETURN = r"""
changed:
  description: Whether the resource was modified.
  type: bool
  returned: always
action:
  description: What happened (C(created), C(updated), C(deleted), C(noop), C(registered), C(would_register)).
  type: str
  returned: always
uuid:
  description: UUID of the affected resource.
  type: str
  returned: when present
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


_BOOL_FIELDS = ('enabled',)
_STR_FIELDS = ('name', 'description', 'email', 'ca', 'custom_ca', 'eab_kid', 'eab_hmac')
_ENUMS = {'ca': ['letsencrypt', 'letsencrypt_test', 'buypass', 'buypass_test', 'google', 'google_test', 'sslcom', 'zerossl', 'custom']}
_REQUIRED = ('name',)
_NO_LOG = ('eab_kid', 'eab_hmac')  # pragma: allowlist secret (field NAMES, not values)


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update({f: {"type": "bool"} for f in _BOOL_FIELDS})
    spec.update(
        {
            f: {
                "type": "str",
                "required": f in _REQUIRED,
                "no_log": f in _NO_LOG,
                **({"choices": _ENUMS[f]} if f in _ENUMS else {}),
            }
            for f in _STR_FIELDS
        }
    )
    spec.update({"state": {"type": "str", "choices": ['present', 'absent', 'registered'], "default": "present"}})
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    # Match key always; other options only when set, so an unset option leaves that
    # field untouched on an existing entry (same contract as the other CRUD modules).
    params: dict = {}
    for field in _BOOL_FIELDS:
        if module.params.get(field) is not None:
            params[field] = "1" if module.params[field] else "0"
    for field in _STR_FIELDS:
        if module.params.get(field) is not None:
            params[field] = module.params[field]

    from opnsense.managers.acme.accounts import AcmeAccountManager

    run_module(module, AcmeAccountManager, params)


if __name__ == "__main__":
    main()
