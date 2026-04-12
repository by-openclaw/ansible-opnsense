#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense trust certificate management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_trust_cert
short_description: Manage OPNsense certificates
version_added: "0.3.0"
description:
  - Create, update, or delete certificate entries on OPNsense.
  - Thin wrapper around lib-opnsense TrustCertManager.ensure().
  - Requires OPNsense >= 26.1.
  - The OPNsense API field "state" (US state/province) collides with Ansible's
    "state" (present/absent). Use the C(province) parameter for the certificate
    state/province field.
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
  descr:
    description: Certificate description (unique identifier / match key).
    type: str
    required: true
  caref:
    description: Signing CA reference UUID.
    type: str
    default: ""
  action:
    description: Certificate action type.
    type: str
    choices: [internal, external, existing]
    default: internal
  key_type:
    description: Key type (e.g. RSA, ECDSA).
    type: str
    default: ""
  digest:
    description: Digest algorithm (e.g. SHA256).
    type: str
    default: ""
  cert_type:
    description: Certificate type.
    type: str
    choices: [usr_cert, server_cert]
    default: server_cert
  lifetime:
    description: Certificate lifetime in days.
    type: int
  commonname:
    description: Common name (CN) for the certificate.
    type: str
    default: ""
  altnames_dns:
    description: Subject alternative names — DNS entries (comma-separated).
    type: str
    default: ""
  altnames_ip:
    description: Subject alternative names — IP addresses (comma-separated).
    type: str
    default: ""
  country:
    description: Country code (C) for the certificate subject.
    type: str
    default: ""
  province:
    description: >
      State or province (ST) for the certificate subject.
      Maps to the OPNsense API field "state".
    type: str
    default: ""
  city:
    description: City / locality (L) for the certificate subject.
    type: str
    default: ""
  organization:
    description: Organization (O) for the certificate subject.
    type: str
    default: ""
  email:
    description: Email address for the certificate subject.
    type: str
    default: ""
  crt_payload:
    description: Existing certificate payload (PEM) when action is "existing".
    type: str
    default: ""
  prv_payload:
    description: Existing private key payload (PEM) when action is "existing".
    type: str
    default: ""
    no_log: true
  csr_payload:
    description: CSR payload (PEM) when action is "external".
    type: str
    default: ""
  state:
    description: Desired state of the certificate.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create an internal server certificate
  by_systems.opnsense.opnsense_trust_cert:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    descr: "Web Server Cert"
    caref: "{{ ca_uuid }}"
    action: internal
    cert_type: server_cert
    key_type: RSA
    digest: SHA256
    lifetime: 365
    commonname: "web.example.com"
    altnames_dns: "web.example.com,www.example.com"
    country: "RO"
    province: "Bucharest"
    organization: "Example Corp"
    state: present

- name: Import an existing certificate
  by_systems.opnsense.opnsense_trust_cert:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    descr: "Imported Cert"
    action: existing
    crt_payload: "{{ lookup('file', 'cert.pem') }}"
    prv_payload: "{{ lookup('file', 'cert-key.pem') }}"
    state: present

- name: Remove a certificate
  by_systems.opnsense.opnsense_trust_cert:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    descr: "Web Server Cert"
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
            "descr": {"type": "str", "required": True},
            "caref": {"type": "str", "default": ""},
            "action": {
                "type": "str",
                "choices": ["internal", "external", "existing"],
                "default": "internal",
            },
            "key_type": {"type": "str", "default": ""},
            "digest": {"type": "str", "default": ""},
            "cert_type": {
                "type": "str",
                "choices": ["usr_cert", "server_cert"],
                "default": "server_cert",
            },
            "lifetime": {"type": "int"},
            "commonname": {"type": "str", "default": ""},
            "altnames_dns": {"type": "str", "default": ""},
            "altnames_ip": {"type": "str", "default": ""},
            "country": {"type": "str", "default": ""},
            "province": {"type": "str", "default": ""},
            "city": {"type": "str", "default": ""},
            "organization": {"type": "str", "default": ""},
            "email": {"type": "str", "default": ""},
            "crt_payload": {"type": "str", "default": ""},
            "prv_payload": {"type": "str", "default": "", "no_log": True},
            "csr_payload": {"type": "str", "default": ""},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {
        "descr": module.params["descr"],
        "action": module.params["action"],
        "cert_type": module.params["cert_type"],
    }
    if module.params["caref"]:
        params["caref"] = module.params["caref"]
    if module.params["key_type"]:
        params["key_type"] = module.params["key_type"]
    if module.params["digest"]:
        params["digest"] = module.params["digest"]
    if module.params["lifetime"] is not None:
        params["lifetime"] = str(module.params["lifetime"])
    if module.params["commonname"]:
        params["commonname"] = module.params["commonname"]
    if module.params["altnames_dns"]:
        params["altnames_dns"] = module.params["altnames_dns"]
    if module.params["altnames_ip"]:
        params["altnames_ip"] = module.params["altnames_ip"]
    if module.params["country"]:
        params["country"] = module.params["country"]
    if module.params["province"]:
        params["state"] = module.params["province"]
    if module.params["city"]:
        params["city"] = module.params["city"]
    if module.params["organization"]:
        params["organization"] = module.params["organization"]
    if module.params["email"]:
        params["email"] = module.params["email"]
    if module.params["crt_payload"]:
        params["crt_payload"] = module.params["crt_payload"]
    if module.params["prv_payload"]:
        params["prv_payload"] = module.params["prv_payload"]
    if module.params["csr_payload"]:
        params["csr_payload"] = module.params["csr_payload"]

    from opnsense.managers.trust.cert import TrustCertManager

    run_module(module, TrustCertManager, params)


if __name__ == "__main__":
    main()
