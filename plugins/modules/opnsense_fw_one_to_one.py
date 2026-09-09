#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense one-to-one NAT rule management."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_fw_one_to_one
short_description: Manage OPNsense one-to-one NAT rules
version_added: "0.2.0"
description:
  - Create, update, or delete one-to-one (binat) NAT rules on OPNsense.
  - Thin wrapper around lib-opnsense FwOneToOneManager.ensure().
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
  description:
    description: Rule description (used as match key).
    type: str
    required: true
  interface:
    description: Interface to apply the rule on.
    type: str
    default: wan
  source_net:
    description: Internal source network (used as match key).
    type: str
    required: true
  external:
    description: External (public) address for the mapping.
    type: str
    default: ""
  disabled:
    description: Whether the rule is disabled.
    type: bool
    default: false
  log:
    description: Log matching packets.
    type: bool
    default: false
  type:
    description: NAT type — binat or nat.
    type: str
    choices: [binat, nat]
    default: binat
  destination_net:
    description: Destination network filter.
    type: str
    default: ""
  natreflection:
    description: NAT reflection mode.
    type: str
    choices: ["", enable, disable]
    default: ""
  state:
    description: Desired state of the rule.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create a one-to-one NAT mapping
  by_systems.opnsense.opnsense_fw_one_to_one:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Web server binat"
    interface: wan
    source_net: "10.6.225.10"
    external: "198.51.100.10"
    state: present

- name: Idempotent check — no changes expected
  by_systems.opnsense.opnsense_fw_one_to_one:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Web server binat"
    interface: wan
    source_net: "10.6.225.10"
    external: "198.51.100.10"
    state: present

- name: Remove a one-to-one NAT rule
  by_systems.opnsense.opnsense_fw_one_to_one:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Web server binat"
    source_net: "10.6.225.10"
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
            "description": {"type": "str", "required": True},
            "interface": {"type": "str", "default": "wan"},
            "source_net": {"type": "str", "required": True},
            "external": {"type": "str", "default": ""},
            "disabled": {"type": "bool", "default": False},
            "log": {"type": "bool", "default": False},
            "type": {
                "type": "str",
                "choices": ["binat", "nat"],
                "default": "binat",
            },
            "destination_net": {"type": "str", "default": ""},
            "natreflection": {
                "type": "str",
                "choices": ["", "enable", "disable"],
                "default": "",
            },
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {
        "description": module.params["description"],
        "interface": module.params["interface"],
        "source_net": module.params["source_net"],
        "type": module.params["type"],
        "disabled": "1" if module.params["disabled"] else "0",
        "log": "1" if module.params["log"] else "0",
    }
    if module.params["external"]:
        params["external"] = module.params["external"]
    if module.params["destination_net"]:
        params["destination_net"] = module.params["destination_net"]
    if module.params["natreflection"]:
        params["natreflection"] = module.params["natreflection"]

    from opnsense.managers.firewall.one_to_one import FwOneToOneManager

    run_module(module, FwOneToOneManager, params)


if __name__ == "__main__":
    main()
