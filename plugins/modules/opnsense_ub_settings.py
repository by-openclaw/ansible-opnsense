#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module for OPNsense Unbound general settings via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ub_settings
short_description: Manage OPNsense Unbound resolver general settings
version_added: "0.5.0"
description:
  - Manage the C(general) block of the Unbound DNS resolver on an OPNsense firewall.
  - Thin wrapper around lib-opnsense UbSettingsManager.ensure().
  - >
    A freshly installed or seeded firewall ships with the resolver DISABLED;
    this module is the API path that turns it on. Only the options you set
    are diffed and sent — everything else is left untouched.
  - Forwards, DNS-over-TLS, ACLs, host overrides and aliases have their own modules.
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
  enabled:
    description: Enable the Unbound resolver.
    type: bool
  listen_port:
    description: Port Unbound listens on (API field C(port)).
    type: str
  active_interface:
    description: Interface slot ids to listen on (empty list = all interfaces).
    type: list
    elements: str
  outgoing_interface:
    description: Interface slot ids used for upstream queries (empty list = all).
    type: list
    elements: str
  stats:
    description: Collect resolver statistics.
    type: bool
  dnssec:
    description: Enable DNSSEC validation.
    type: bool
  dns64:
    description: Enable DNS64 synthesis.
    type: bool
  dns64prefix:
    description: DNS64 prefix (blank = default C(64:ff9b::/96)).
    type: str
  noarecords:
    description: Do not return A records (IPv6-only networks).
    type: bool
  regdhcp:
    description: Register DHCP leases in DNS.
    type: bool
  regdhcpdomain:
    description: Domain suffix for registered DHCP names.
    type: str
  regdhcpstatic:
    description: Register static DHCP mappings in DNS.
    type: bool
  noreglladdr6:
    description: Do not register IPv6 link-local addresses.
    type: bool
  noregrecords:
    description: Do not register system A/AAAA records.
    type: bool
  txtsupport:
    description: Register DHCP client descriptions as TXT records.
    type: bool
  cacheflush:
    description: Flush the cache on every reload.
    type: bool
  safesearch:
    description: Force SafeSearch on major search engines.
    type: bool
  enable_wpad:
    description: Serve WPAD records.
    type: bool
  local_zone_type:
    description: Local zone type.
    type: str
    choices:
      - always_nxdomain
      - always_refuse
      - always_transparent
      - deny
      - inform
      - inform_deny
      - nodefault
      - refuse
      - static
      - transparent
      - typetransparent
  state:
    description: Only C(present) is supported (singleton settings).
    type: str
    choices: [present]
    default: present
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Turn the resolver on for every interface (fresh firewall)
  by_systems.opnsense.opnsense_ub_settings:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    enabled: true
    listen_port: "53"

- name: Listen only on the internal slots, validate DNSSEC
  by_systems.opnsense.opnsense_ub_settings:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    enabled: true
    active_interface: [lan, opt2]
    dnssec: true
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
  description: Before/after C(general) settings.
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
    "stats",
    "dnssec",
    "dns64",
    "noarecords",
    "regdhcp",
    "regdhcpstatic",
    "noreglladdr6",
    "noregrecords",
    "txtsupport",
    "cacheflush",
    "safesearch",
    "enable_wpad",
)
_STR_FIELDS = ("dns64prefix", "regdhcpdomain", "local_zone_type")
# Multi-selects: the manager normalises a list to the CSV the API expects.
_LIST_FIELDS = ("active_interface", "outgoing_interface")
_LOCAL_ZONE_TYPES = [
    "always_nxdomain",
    "always_refuse",
    "always_transparent",
    "deny",
    "inform",
    "inform_deny",
    "nodefault",
    "refuse",
    "static",
    "transparent",
    "typetransparent",
]


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update({f: {"type": "bool"} for f in _BOOL_FIELDS})
    spec.update({f: {"type": "str"} for f in _STR_FIELDS if f != "local_zone_type"})
    spec.update({f: {"type": "list", "elements": "str"} for f in _LIST_FIELDS})
    spec.update(
        {
            # `port` is taken by the API connection port; the resolver port is
            # exposed as listen_port and mapped to the API field `port`.
            "listen_port": {"type": "str"},
            "local_zone_type": {"type": "str", "choices": _LOCAL_ZONE_TYPES},
            "state": {"type": "str", "choices": ["present"], "default": "present"},
        }
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    # Only send what the caller actually set: the manager diffs solely the keys
    # it receives, so an unset option leaves that setting untouched.
    params: dict = {}
    for field in _BOOL_FIELDS:
        if module.params.get(field) is not None:
            params[field] = "1" if module.params[field] else "0"
    for field in _STR_FIELDS:
        if module.params.get(field) is not None:
            params[field] = module.params[field]
    for field in _LIST_FIELDS:
        if module.params.get(field) is not None:
            params[field] = list(module.params[field])
    if module.params.get("listen_port") is not None:
        params["port"] = module.params["listen_port"]

    from opnsense.managers.dns.ub_settings import UbSettingsManager

    run_module(module, UbSettingsManager, params)


if __name__ == "__main__":
    main()
