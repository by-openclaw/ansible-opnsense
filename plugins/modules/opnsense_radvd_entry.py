#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_radvd_entry — thin wrapper on lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_radvd_entry
short_description: Manage OPNsense radvd per-interface router advertisement entries
version_added: "0.5.0"
description:
  - CRUD for radvd entries (matched by I(interface)) — lib-opnsense RadvdEntryManager.ensure().
  - Kea DHCPv6 emits no router advertisements; one entry per served interface is required.
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
  interface:
    description: Interface slot id (match key).
    type: str
    required: true
  enabled:
    description: Enable the entry.
    type: bool
  mode:
    description: Advertisement mode.
    type: str
    choices: [router, unmanaged, managed, assist, stateless]
  base6_interface:
    description: Track this interface's prefix (API field C(Base6Interface)).
    type: str
  deprecate_prefix:
    description: Deprecate the prefix on change (C(on)/C(off), empty = default).
    type: str
    choices: ["", "on", "off"]
  remove_adv_on_exit:
    description: Withdraw advertisements on exit (API field C(RemoveAdvOnExit)).
    type: str
    choices: ["", "on", "off"]
  remove_route:
    description: Remove the route on exit (API field C(RemoveRoute)).
    type: str
    choices: ["", "on", "off"]
  advertise_dns:
    description:
      - >
        Advertise DNS configuration in the router advertisement (API field C(dns)).
      - >
        With this on and I(rdnss) EMPTY, radvd advertises the interface's own address, so
        IPv6 clients resolve at the firewall whatever DHCPv4 hands out. Set I(rdnss) to
        point them somewhere specific.
    type: bool
  rdnss:
    description:
      - >
        Recursive DNS servers to advertise (RFC 8106, API field C(RDNSS)) — up to three
        IPv6 addresses, comma separated. This is what gives IPv6 clients the same resolver
        as IPv4.
    type: str
  dnssl:
    description: DNS search domain list to advertise (RFC 8106, API field C(DNSSL)).
    type: str
  rdnss_lifetime:
    description: Lifetime for the advertised resolvers, in seconds (API field C(AdvRDNSSLifetime)).
    type: str
  dnssl_lifetime:
    description: Lifetime for the advertised search list, in seconds (API field C(AdvDNSSLLifetime)).
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
- name: Unmanaged RAs on the MGMT VLAN (Kea6 hands out addresses)
  by_systems.opnsense.opnsense_radvd_entry:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    interface: opt2
    mode: unmanaged
    enabled: true

- name: Point IPv6 clients at the same filtering resolver IPv4 clients use
  by_systems.opnsense.opnsense_radvd_entry:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    interface: opt2
    enabled: true
    advertise_dns: true
    rdnss: "fd01:3::101"
"""

RETURN = r"""
changed:
  description: Whether state on the firewall was modified.
  type: bool
  returned: always
action:
  description: One of C(created), C(updated), C(deleted) or C(noop).
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


_API_NAMES = {
    "advertise_dns": "dns",
    "rdnss": "RDNSS",
    "dnssl": "DNSSL",
    "rdnss_lifetime": "AdvRDNSSLifetime",
    "dnssl_lifetime": "AdvDNSSLLifetime",
    "base6_interface": "Base6Interface",
    "deprecate_prefix": "DeprecatePrefix",
    "remove_adv_on_exit": "RemoveAdvOnExit",
    "remove_route": "RemoveRoute",
}


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update(
        {
            "interface": {"type": "str", "required": True},
            "enabled": {"type": "bool"},
            "mode": {
                "type": "str",
                "choices": ["router", "unmanaged", "managed", "assist", "stateless"],
            },
            "advertise_dns": {"type": "bool"},
            "rdnss": {"type": "str"},
            "dnssl": {"type": "str"},
            "rdnss_lifetime": {"type": "str"},
            "dnssl_lifetime": {"type": "str"},
            "base6_interface": {"type": "str"},
            "deprecate_prefix": {"type": "str", "choices": ["", "on", "off"]},
            "remove_adv_on_exit": {"type": "str", "choices": ["", "on", "off"]},
            "remove_route": {"type": "str", "choices": ["", "on", "off"]},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {"interface": module.params["interface"]}
    for flag in ("enabled", "advertise_dns"):
        if module.params.get(flag) is not None:
            params[_API_NAMES.get(flag, flag)] = "1" if module.params[flag] else "0"
    for field in (
        "mode",
        "rdnss",
        "dnssl",
        "rdnss_lifetime",
        "dnssl_lifetime",
        "base6_interface",
        "deprecate_prefix",
        "remove_adv_on_exit",
        "remove_route",
    ):
        if module.params.get(field) is not None:
            params[_API_NAMES.get(field, field)] = module.params[field]

    from opnsense.managers.services.radvd_entry import RadvdEntryManager

    run_module(module, RadvdEntryManager, params)


if __name__ == "__main__":
    main()
