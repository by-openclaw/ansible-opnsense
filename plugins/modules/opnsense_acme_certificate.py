#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_acme_certificate — thin wrapper on lib-opnsense (AcmeCertificateManager)."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_acme_certificate
short_description: Manage OPNsense ACME certificates (object + issuance)
version_added: "0.6.0"
description:
  - CRUD for ACME certificates (matched by I(name)) — lib-opnsense AcmeCertificateManager.ensure().
  - >
    C(state=issued) = present + sign when the object has no issued leaf yet (C(certRefId) empty or
    last status not C(200)); an issued, unchanged certificate is a noop. I(renew=true) signs again
    (explicit renewal, never idempotent). Signing talks to the CA and can take minutes (DNS-01).
  - I(account), I(validation_method) and I(restart_actions) take the UUIDs of the referenced objects (look them up read-only first).
  - >
    The trust-store refid the issued leaf lands under (C(certRefId)) is read-only on the API:
    binding the WebGUI to it is done in the seed (pre-set refid), not by this module.
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
  name:
    description: Certificate name = primary domain (match key).
    type: str
    required: true
  description:
    description: Free-text description.
    type: str
  alt_names:
    description: Subject Alternative Names (comma-separated).
    type: str
  account:
    description: UUID of the ACME account.
    type: str
  validation_method:
    description: UUID of the validation method.
    type: str
  key_length:
    description: Key type/length.
    type: str
    choices: [key_2048, key_3072, key_4096, key_ec256, key_ec384]
  ocsp:
    description: OCSP Must-Staple.
    type: bool
  profile:
    description: ACME profile name (CA-specific).
    type: str
  restart_actions:
    description: UUID(s) of post-issue actions (comma-separated).
    type: str
  auto_renewal:
    description: Auto-renew this certificate.
    type: bool
  renew_interval:
    description: Renew when this many days remain.
    type: str
  aliasmode:
    description: Alias mode.
    type: str
    choices: [none, automatic, domain, challenge]
  domainalias:
    description: Domain alias (I(aliasmode=domain)).
    type: str
  challengealias:
    description: Challenge alias (I(aliasmode=challenge)).
    type: str
  enabled:
    description: Enable the certificate.
    type: bool
  renew:
    description: "With I(state=issued): sign again even if already issued (explicit renewal)."
    type: bool
    default: false
  state:
    description: Desired state.
    type: str
    choices: [present, absent, issued]
    default: present
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: GUI certificate, issued once and then left alone
  by_systems.opnsense.opnsense_acme_certificate:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: fw.example.com
    account: "{{ acme_account_uuid }}"
    validation_method: "{{ acme_validation_uuid }}"
    restart_actions: "{{ acme_action_uuid }}"
    key_length: key_ec256
    auto_renewal: true
    renew_interval: "30"
    state: issued

- name: Renew now (deliberate, never idempotent)
  by_systems.opnsense.opnsense_acme_certificate:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: fw.example.com
    state: issued
    renew: true
"""

RETURN = r"""
changed:
  description: Whether the resource was modified.
  type: bool
  returned: always
action:
  description: What happened (C(created), C(updated), C(deleted), C(noop), C(issued), C(renewed), C(would_issued), C(would_renewed)).
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


_BOOL_FIELDS = ('ocsp', 'auto_renewal', 'enabled')
_STR_FIELDS = ('name', 'description', 'alt_names', 'account', 'validation_method', 'key_length', 'profile', 'restart_actions', 'renew_interval', 'aliasmode', 'domainalias', 'challengealias')
_ENUMS = {'key_length': ['key_2048', 'key_3072', 'key_4096', 'key_ec256', 'key_ec384'], 'aliasmode': ['none', 'automatic', 'domain', 'challenge']}
_API_NAMES = {
    "alt_names": "altNames",
    "validation_method": "validationMethod",
    "key_length": "keyLength",
    "restart_actions": "restartActions",
    "auto_renewal": "autoRenewal",
    "renew_interval": "renewInterval",
}
_REQUIRED = ('name',)
_NO_LOG = ()  # pragma: allowlist secret (field NAMES, not values)


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
    spec.update({"state": {"type": "str", "choices": ['present', 'absent', 'issued'], "default": "present"}})
    spec.update({"renew": {"type": "bool", "default": False}})
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    # Match key always; other options only when set, so an unset option leaves that
    # field untouched on an existing entry (same contract as the other CRUD modules).
    params: dict = {}
    for field in _BOOL_FIELDS:
        if module.params.get(field) is not None:
            params[_API_NAMES.get(field, field)] = "1" if module.params[field] else "0"
    for field in _STR_FIELDS:
        if module.params.get(field) is not None:
            params[_API_NAMES.get(field, field)] = module.params[field]

    from opnsense.managers.acme.certificates import AcmeCertificateManager

    run_module(module, AcmeCertificateManager, params, ensure_kwargs={"renew": bool(module.params.get("renew"))})


if __name__ == "__main__":
    main()
