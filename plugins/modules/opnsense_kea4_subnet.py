#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense Kea DHCPv4 subnet management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_kea4_subnet
short_description: Manage OPNsense Kea DHCPv4 subnets
version_added: "0.3.0"
description:
  - Create, update, or delete Kea DHCPv4 subnets on OPNsense.
  - Thin wrapper around lib-opnsense Kea4SubnetManager.ensure().
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
  subnet:
    description: >
      Subnet in CIDR notation (e.g. 10.6.225.0/24). Match key.
    type: str
    required: true
  pools:
    description: >
      DHCP pool ranges (e.g. "10.6.225.100-10.6.225.200").
    type: str
    default: ""
  next_server:
    description: Next server (TFTP/PXE boot server) IP address.
    type: str
    default: ""
  description:
    description: Subnet description.
    type: str
    default: ""
  option_data:
    description: DHCP options for the subnet (routers, domain_name_servers, domain_search, domain_name, ntp_servers, time_servers, static_routes, classless_static_route, tftp_server_name, boot_file_name). Diffed sub-key by sub-key.
    type: dict
  match_client_id:
    description: Match clients by client-id (API field C(match-client-id)).
    type: bool
  state:
    description: Desired state of the subnet.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 1.0.0)
"""

EXAMPLES = r"""
- name: Create a DHCPv4 subnet
  by_systems.opnsense.opnsense_kea4_subnet:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    subnet: "10.6.225.0/24"
    pools: "10.6.225.100-10.6.225.200"
    description: "LAN DHCP pool"
    state: present

- name: Remove a DHCPv4 subnet
  by_systems.opnsense.opnsense_kea4_subnet:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    subnet: "10.6.225.0/24"
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
            "subnet": {"type": "str", "required": True},
            "pools": {"type": "str", "default": ""},
            "next_server": {"type": "str", "default": ""},
            "description": {"type": "str", "default": ""},
            "option_data": {"type": "dict"},
            "match_client_id": {"type": "bool"},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {
        "subnet": module.params["subnet"],
    }
    if module.params["pools"]:
        params["pools"] = module.params["pools"]
    if module.params["next_server"]:
        params["next_server"] = module.params["next_server"]
    if module.params["description"]:
        params["description"] = module.params["description"]

    if module.params.get("option_data") is not None:
        params["option_data"] = {
            k: str(v) for k, v in module.params["option_data"].items()
        }
    if module.params.get("match_client_id") is not None:
        params["match-client-id"] = "1" if module.params["match_client_id"] else "0"
    from opnsense.managers.dhcp.kea4_subnet import Kea4SubnetManager

    run_module(module, Kea4SubnetManager, params)


if __name__ == "__main__":
    main()
