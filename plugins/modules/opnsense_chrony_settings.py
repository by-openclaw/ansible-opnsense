#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module for OPNsense os-chrony general settings via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_chrony_settings
short_description: Manage OPNsense Chrony NTP (os-chrony) general settings
version_added: "0.5.0"
description:
  - Manage the general settings of the os-chrony plugin (client-only unless I(allowed_networks) is set).
  - Thin wrapper around lib-opnsense ChronyGeneralManager.ensure().
  - Chrony replaces the base ntpd — stop ntpd separately.
  - Only the options you set are diffed and sent — everything else is left untouched.
  - Requires OPNsense >= 26.1 and the os-chrony plugin.
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
  enabled:
    description: Enable chronyd.
    type: bool
  ntp_port:
    description: NTP port (API field C(port); 123 to serve clients).
    type: str
  nts_client:
    description: Use NTS for upstream peers.
    type: bool
  nts_nocert:
    description: Skip NTS certificate validation.
    type: bool
  peers:
    description: Upstream NTP peers (pool hostnames).
    type: list
    elements: str
  fallback_peers:
    description: Fallback peers (CSV).
    type: str
  allowed_networks:
    description: Networks chronyd serves NTP to (empty = client-only).
    type: list
    elements: str
  state:
    description: Only C(present) is supported (singleton settings).
    type: str
    choices: [present]
    default: present
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Manage OPNsense Chrony NTP (os-chrony) general settings
  by_systems.opnsense.opnsense_chrony_settings:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    enabled: true
    ntp_port: "123"
    peers: [0.be.pool.ntp.org, 1.be.pool.ntp.org]
    allowed_networks: ["10.1.0.0/16", "fd01::/32"]
"""

RETURN = r"""
changed:
  description: Whether any setting drifted.
  type: bool
  returned: always
action:
  description: One of C(updated) or C(noop).
  type: str
  returned: always
diff:
  description: Before/after settings.
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

# API booleans are the strings "0"/"1", not JSON booleans.
_BOOL_FIELDS = ("enabled", "nts_client", "nts_nocert")
_STR_FIELDS = ("ntp_port", "fallback_peers")
# Multi-selects: the manager normalises a list to the CSV the API expects.
_LIST_FIELDS = ("peers", "allowed_networks")
# Module option -> API field (only where they differ).
_API_NAMES = {
    "ntp_port": "port",
    "nts_client": "ntsclient",
    "nts_nocert": "ntsnocert",
    "fallback_peers": "fallbackpeers",
    "allowed_networks": "allowednetworks",
}


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update({f: {"type": "bool"} for f in _BOOL_FIELDS})
    spec.update({f: {"type": "str"} for f in _STR_FIELDS})
    spec.update({f: {"type": "list", "elements": "str"} for f in _LIST_FIELDS})
    spec.update(
        {"state": {"type": "str", "choices": ["present"], "default": "present"}}
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    # Only send what the caller actually set: the manager diffs solely the keys
    # it receives, so an unset option leaves that setting untouched.
    params: dict = {}
    for field in _BOOL_FIELDS:
        if module.params.get(field) is not None:
            params[_API_NAMES.get(field, field)] = "1" if module.params[field] else "0"
    for field in _STR_FIELDS:
        if module.params.get(field) is not None:
            params[_API_NAMES.get(field, field)] = module.params[field]
    for field in _LIST_FIELDS:
        if module.params.get(field) is not None:
            params[_API_NAMES.get(field, field)] = list(module.params[field])

    from opnsense.managers.services.chrony_general import ChronyGeneralManager

    run_module(module, ChronyGeneralManager, params)


if __name__ == "__main__":
    main()
