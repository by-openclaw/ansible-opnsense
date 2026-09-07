#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module for OPNsense os-dnscrypt-proxy general settings via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_dnscrypt_settings
short_description: Manage OPNsense dnscrypt-proxy (os-dnscrypt-proxy) general settings
version_added: "0.5.0"
description:
  - Manage the general settings of the os-dnscrypt-proxy plugin — the encrypted upstream of the Unbound chain.
  - Thin wrapper around lib-opnsense DnscryptProxyGeneralManager.ensure().
  - >
    I(serverlist) / I(disabled_serverlist) / I(relaylist) are free-form CSV lists of server NAMES from
    the public-resolvers list the daemon downloads; the API does not validate them against that list,
    so the whole configuration converges in one call (unknown names are ignored by the daemon).
  - Only the options you set are diffed and sent — everything else is left untouched.
  - Requires OPNsense >= 26.1 and the os-dnscrypt-proxy plugin.
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
    description: Enable dnscrypt-proxy.
    type: bool
  listen_addresses:
    description: Listen addresses (e.g. 127.0.0.1:53531, [::1]:53531).
    type: list
    elements: str
  serverlist:
    description: Upstream server names from the public-resolvers list (free-form; not validated by the API).
    type: list
    elements: str
  disabled_serverlist:
    description: Server names to exclude.
    type: list
    elements: str
  relaylist:
    description: Anonymized DNS relays.
    type: list
    elements: str
  ipv4_servers:
    description: Use IPv4 upstream servers.
    type: bool
  ipv6_servers:
    description: Use IPv6 upstream servers.
    type: bool
  dnscrypt_servers:
    description: Use DNSCrypt servers.
    type: bool
  doh_servers:
    description: Use DoH servers.
    type: bool
  odoh_servers:
    description: Use ODoH servers.
    type: bool
  require_dnssec:
    description: Only DNSSEC-validating servers.
    type: bool
  require_nolog:
    description: Only no-log servers.
    type: bool
  require_nofilter:
    description: Only non-filtering servers.
    type: bool
  force_tcp:
    description: Force TCP upstream.
    type: bool
  cache:
    description: Enable the local cache.
    type: bool
  cache_size:
    description: Cache size (entries).
    type: str
  cache_min_ttl:
    description: Cache min TTL.
    type: str
  cache_max_ttl:
    description: Cache max TTL.
    type: str
  cache_neg_min_ttl:
    description: Negative cache min TTL.
    type: str
  cache_neg_max_ttl:
    description: Negative cache max TTL.
    type: str
  fallback_resolver:
    description: Bootstrap resolver (ip:port).
    type: str
  timeout:
    description: Query timeout (ms).
    type: str
  keepalive:
    description: Keepalive (s).
    type: str
  cert_refresh_delay:
    description: Certificate refresh delay (min).
    type: str
  query_logs:
    description: Log every query (audit).
    type: bool
  block_ipv6:
    description: Block AAAA answers.
    type: bool
  allow_privileged:
    description: Allow binding privileged ports.
    type: bool
  max_clients:
    description: Max concurrent clients.
    type: str
  dnscrypt_ephemeral_keys:
    description: Ephemeral DNSCrypt keys.
    type: bool
  tls_disable_session_tickets:
    description: Disable TLS session tickets.
    type: bool
  proxy:
    description: SOCKS proxy URL.
    type: str
  state:
    description: Only C(present) is supported (singleton settings).
    type: str
    choices: [present]
    default: present
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Manage OPNsense dnscrypt-proxy (os-dnscrypt-proxy) general settings
  by_systems.opnsense.opnsense_dnscrypt_settings:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    enabled: true
    listen_addresses: ["127.0.0.1:53531", "[::1]:53531"]
    require_dnssec: true
    require_nolog: true
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
_BOOL_FIELDS = (
    "enabled",
    "ipv4_servers",
    "ipv6_servers",
    "dnscrypt_servers",
    "doh_servers",
    "odoh_servers",
    "require_dnssec",
    "require_nolog",
    "require_nofilter",
    "force_tcp",
    "cache",
    "query_logs",
    "block_ipv6",
    "allow_privileged",
    "dnscrypt_ephemeral_keys",
    "tls_disable_session_tickets",
)
_STR_FIELDS = (
    "cache_size",
    "cache_min_ttl",
    "cache_max_ttl",
    "cache_neg_min_ttl",
    "cache_neg_max_ttl",
    "fallback_resolver",
    "timeout",
    "keepalive",
    "cert_refresh_delay",
    "max_clients",
    "proxy",
)
# Multi-selects: the manager normalises a list to the CSV the API expects.
_LIST_FIELDS = ("listen_addresses", "serverlist", "disabled_serverlist", "relaylist")
# Module option -> API field (only where they differ).
_API_NAMES = {"allow_privileged": "allowprivileged"}


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

    from opnsense.managers.dns.dnscrypt_general import DnscryptProxyGeneralManager

    run_module(module, DnscryptProxyGeneralManager, params)


if __name__ == "__main__":
    main()
