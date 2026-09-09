#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_kea4_settings — thin wrapper on lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_kea4_settings
short_description: Manage OPNsense Kea DHCPv4 general settings
version_added: "0.5.0"
description:
  - Manage the C(general) block of Kea DHCPv4 — lib-opnsense Kea4SettingsManager.ensure().
  - >
    A freshly seeded firewall ships Kea disabled; this enables it and binds the listening interfaces. Only the options you set are diffed and sent.
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
    description: Enable the Kea DHCP daemon for this address family.
    type: bool
  fwrules:
    description: Let the plugin add its own firewall pass rules.
    type: bool
  manual_config:
    description: Use a hand-written kea config instead of the generated one.
    type: bool
  valid_lifetime:
    description: Lease valid lifetime (s).
    type: str
  decline_probation_period:
    description: Decline probation period (s).
    type: str
  service_sockets_max_retries:
    description: Socket bind retries.
    type: str
  service_sockets_retry_wait_time:
    description: Socket bind retry wait (ms).
    type: str
  interfaces:
    description: Interface slot ids the daemon listens on.
    type: list
    elements: str
  dhcp_socket_type:
    description: Socket type.
    type: str
    choices: ['raw', 'udp']
  compatibility:
    description: Compatibility flags (exclude-first-last-24, ignore-dhcp-server-identifier, ignore-rai-link-selection, lenient-option-parsing).
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
- name: Enable Kea DHCPv4 on the internal VLANs
  by_systems.opnsense.opnsense_kea4_settings:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    enabled: true
    fwrules: false
    valid_lifetime: "4000"
    interfaces: [opt2, opt3, opt4]
"""

RETURN = r"""
changed:
  description: Whether state on the firewall was modified.
  type: bool
  returned: always
action:
  description: One of C(updated) or C(noop).
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


_BOOL_FIELDS = ("enabled", "fwrules", "manual_config")
_STR_FIELDS = (
    "valid_lifetime",
    "decline_probation_period",
    "service_sockets_max_retries",
    "service_sockets_retry_wait_time",
    "dhcp_socket_type",
)
_LIST_FIELDS = ("interfaces", "compatibility")
_ENUMS = {"dhcp_socket_type": ["raw", "udp"]}
_API_NAMES = {}


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update({f: {"type": "bool"} for f in _BOOL_FIELDS})
    spec.update(
        {
            f: {"type": "str", **({"choices": _ENUMS[f]} if f in _ENUMS else {})}
            for f in _STR_FIELDS
        }
    )
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

    from opnsense.managers.dhcp.kea4_settings import Kea4SettingsManager

    run_module(module, Kea4SettingsManager, params)


if __name__ == "__main__":
    main()
