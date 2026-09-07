#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_dnsmasq_settings — thin wrapper on lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_dnsmasq_settings
short_description: Manage OPNsense Dnsmasq global settings
version_added: "0.5.0"
description:
  - Manage the Dnsmasq global settings singleton — lib-opnsense DnsmasqSettingsManager.ensure().
  - >
    Dnsmasq holds 67/547 globally unless I(strictbind) is set; keep it disabled or strictly bound while Kea runs. Sub-resources (hosts, ranges, domains, options, boot, tags) have their own managers.
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
  enable:
    description: Master enable flag.
    type: bool
  regdhcp:
    description: Register DHCP leases in DNS.
    type: bool
  regdhcpstatic:
    description: Register static DHCP mappings.
    type: bool
  dhcpfirst:
    description: Resolve DHCP hosts before upstream.
    type: bool
  strict_order:
    description: Query upstream servers in strict order.
    type: bool
  domain_needed:
    description: Drop reverse lookups without a domain.
    type: bool
  no_private_reverse:
    description: Drop RFC1918 reverse lookups.
    type: bool
  no_resolv:
    description: Ignore /etc/resolv.conf.
    type: bool
  log_queries:
    description: Log every query.
    type: bool
  no_hosts:
    description: Ignore /etc/hosts.
    type: bool
  strictbind:
    description: Bind only to the listed interfaces.
    type: bool
  dnssec:
    description: DNSSEC validation.
    type: bool
  add_subnet:
    description: Add EDNS client subnet.
    type: bool
  strip_subnet:
    description: Strip EDNS client subnet.
    type: bool
  no_ident:
    description: Do not answer ident queries.
    type: bool
  regdhcpdomain:
    description: Domain suffix for registered DHCP names.
    type: str
  interface:
    description: Interface slot ids to bind.
    type: list
    elements: str
  listen_port:
    description: Listening port (API field C(port); e.g. 53053 when Unbound owns 53).
    type: str
  dns_port:
    description: DNS port.
    type: str
  dns_forward_max:
    description: Max concurrent forwards.
    type: str
  cache_size:
    description: Cache size.
    type: str
  local_ttl:
    description: Local TTL.
    type: str
  add_mac:
    description: Add MAC to forwarded queries.
    type: str
    choices: ['', 'standard', 'base64', 'text']
  dhcp:
    description: DHCP interface slot ids.
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
- name: Keep Dnsmasq off (Kea owns DHCP, Unbound owns DNS)
  by_systems.opnsense.opnsense_dnsmasq_settings:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    enable: false
    strictbind: true
    listen_port: "53053"
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


_BOOL_FIELDS = (
    "enable",
    "regdhcp",
    "regdhcpstatic",
    "dhcpfirst",
    "strict_order",
    "domain_needed",
    "no_private_reverse",
    "no_resolv",
    "log_queries",
    "no_hosts",
    "strictbind",
    "dnssec",
    "add_subnet",
    "strip_subnet",
    "no_ident",
)
_STR_FIELDS = (
    "regdhcpdomain",
    "listen_port",
    "dns_port",
    "dns_forward_max",
    "cache_size",
    "local_ttl",
    "add_mac",
)
_LIST_FIELDS = ("interface", "dhcp")
_ENUMS = {"add_mac": ["", "standard", "base64", "text"]}
_API_NAMES = {"listen_port": "port"}


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

    from opnsense.managers.services.dnsmasq_settings import DnsmasqSettingsManager

    run_module(module, DnsmasqSettingsManager, params)


if __name__ == "__main__":
    main()
