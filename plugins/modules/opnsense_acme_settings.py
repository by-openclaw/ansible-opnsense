#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_acme_settings — thin wrapper on lib-opnsense (AcmeSettingsManager)."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_acme_settings
short_description: Manage OPNsense ACME client general settings
version_added: "0.6.0"
description:
  - Singleton settings of C(os-acme-client) — lib-opnsense AcmeSettingsManager.ensure(). Only the options you set are diffed and sent.
  - The lib applies C(acmeclient/service/reconfigure) after a change (regenerates the acme.sh config).
  - >
    I(cron=true) also converges the auto-renewal cron job through the plugin's own
    C(settings/fetchCronIntegration) — the ONLY way it creates that job; saving I(auto_renewal)
    through the API alone leaves the firewall without renewals. Idempotent (C(no change) = noop).
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
  enabled:
    description: Master enable of the ACME client.
    type: bool
  auto_renewal:
    description: Enable the auto-renewal cron.
    type: bool
  environment:
    description: ACME environment (empty = default, C(prod), C(stg)).
    type: str
    choices: ["", prod, stg]
  challenge_port:
    description: Internal HTTP-01 challenge port.
    type: str
  tls_challenge_port:
    description: Internal TLS-ALPN-01 challenge port.
    type: str
  restart_timeout:
    description: Seconds to wait for service restarts.
    type: str
  haproxy_integration:
    description: Enable HAProxy integration.
    type: bool
  log_level:
    description: acme.sh log level.
    type: str
    choices: [normal, extended, debug, debug2, debug3]
  show_intro:
    description: Show the GUI intro panel.
    type: bool
  cron:
    description: Ensure the auto-renewal cron job exists (requires I(enabled) and I(auto_renewal)).
    type: bool
    default: false
  state:
    description: Always C(present).
    type: str
    choices: [present]
    default: present
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Enable the ACME client with auto-renewal
  by_systems.opnsense.opnsense_acme_settings:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    enabled: true
    auto_renewal: true
    environment: prod
    cron: true
"""

RETURN = r"""
changed:
  description: Whether the settings were modified.
  type: bool
  returned: always
action:
  description: C(updated), C(cron_created) or C(noop).
  type: str
  returned: always
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


_BOOL_FIELDS = ("enabled", "auto_renewal", "haproxy_integration", "show_intro")
_STR_FIELDS = ("environment", "challenge_port", "tls_challenge_port", "restart_timeout", "log_level")
_ENUMS = {"environment": ["", "prod", "stg"], "log_level": ["normal", "extended", "debug", "debug2", "debug3"]}
_API_NAMES = {
    "auto_renewal": "autoRenewal",
    "challenge_port": "challengePort",
    "tls_challenge_port": "TLSchallengePort",
    "restart_timeout": "restartTimeout",
    "haproxy_integration": "haproxyIntegration",
    "log_level": "logLevel",
    "show_intro": "showIntro",
}


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update({f: {"type": "bool"} for f in _BOOL_FIELDS})
    spec.update(
        {f: {"type": "str", **({"choices": _ENUMS[f]} if f in _ENUMS else {})} for f in _STR_FIELDS}
    )
    spec.update({"state": {"type": "str", "choices": ["present"], "default": "present"}})
    spec.update({"cron": {"type": "bool", "default": False}})
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {}
    for field in _BOOL_FIELDS:
        if module.params.get(field) is not None:
            params[_API_NAMES.get(field, field)] = "1" if module.params[field] else "0"
    for field in _STR_FIELDS:
        if module.params.get(field) is not None:
            params[_API_NAMES.get(field, field)] = module.params[field]

    from opnsense.managers.acme.settings import AcmeSettingsManager

    run_module(module, AcmeSettingsManager, params, ensure_kwargs={"cron": bool(module.params.get("cron"))})


if __name__ == "__main__":
    main()
