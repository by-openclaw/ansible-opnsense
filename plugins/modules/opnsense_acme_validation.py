#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_acme_validation — thin wrapper on lib-opnsense (AcmeValidationManager)."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_acme_validation
short_description: Manage OPNsense ACME challenge (validation) methods
version_added: "0.6.0"
description:
  - CRUD for ACME validation methods (matched by I(name)) — lib-opnsense AcmeValidationManager.ensure().
  - Cloudflare DNS-01 = I(method=dns01), I(dns_service=dns_cf), I(dns_cf_token) (scoped token; preferred over the legacy global key).
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
    description: Validation name (match key).
    type: str
    required: true
  description:
    description: Free-text description.
    type: str
  method:
    description: Challenge type.
    type: str
    choices: [http01, dns01, tlsalpn01]
  enabled:
    description: Enable the method.
    type: bool
  http_service:
    description: HTTP-01 server.
    type: str
    choices: [opnsense, haproxy]
  http_opn_autodiscovery:
    description: Auto-detect the HTTP-01 interface.
    type: bool
  http_opn_interface:
    description: HTTP-01 listen interface.
    type: str
  http_opn_ipaddresses:
    description: HTTP-01 listen IP(s).
    type: str
  dns_service:
    description: acme.sh DNS provider id (C(dns_cf) = Cloudflare).
    type: str
  dns_sleep:
    description: Seconds to wait for DNS propagation.
    type: str
  dns_cf_email:
    description: Cloudflare account e-mail (legacy global-key auth).
    type: str
  dns_cf_key:
    description: Cloudflare global API key (legacy auth).
    type: str
    no_log: true
  dns_cf_token:
    description: Cloudflare scoped API token (preferred).
    type: str
    no_log: true
  dns_cf_account_id:
    description: Cloudflare account id.
    type: str
  dns_cf_zone_id:
    description: Cloudflare zone id (optional).
    type: str
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Cloudflare DNS-01 challenge
  by_systems.opnsense.opnsense_acme_validation:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: cloudflare-dns
    method: dns01
    dns_service: dns_cf
    dns_cf_token: "{{ cloudflare_api_token }}"
    dns_cf_account_id: "{{ cloudflare_account_id }}"
    dns_sleep: "30"
"""

RETURN = r"""
changed:
  description: Whether the resource was modified.
  type: bool
  returned: always
action:
  description: What happened (C(created), C(updated), C(deleted), C(noop)).
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


_BOOL_FIELDS = ("enabled", "http_opn_autodiscovery")
_STR_FIELDS = (
    "name",
    "description",
    "method",
    "http_service",
    "http_opn_interface",
    "http_opn_ipaddresses",
    "dns_service",
    "dns_sleep",
    "dns_cf_email",
    "dns_cf_key",
    "dns_cf_token",
    "dns_cf_account_id",
    "dns_cf_zone_id",
)
_ENUMS = {
    "method": ["http01", "dns01", "tlsalpn01"],
    "http_service": ["opnsense", "haproxy"],
}
_REQUIRED = ("name",)
_NO_LOG = (
    "dns_cf_key",
    "dns_cf_token",
)  # pragma: allowlist secret (field NAMES, not values)


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
    spec.update(
        {
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            }
        }
    )
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

    from opnsense.managers.acme.validations import AcmeValidationManager

    run_module(module, AcmeValidationManager, params)


if __name__ == "__main__":
    main()
