#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense NPTv6 (Network Prefix Translation) management."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_fw_npt
short_description: Manage OPNsense NPTv6 rules
version_added: "0.2.0"
description:
  - Create, update, or delete NPTv6 (Network Prefix Translation) rules on OPNsense.
  - Thin wrapper around lib-opnsense FwNptManager.ensure().
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
  source_net:
    description: Internal IPv6 source prefix (used as match key).
    type: str
    required: true
  destination_net:
    description: External IPv6 destination prefix (used as match key).
    type: str
    required: true
  interface:
    description: Interface to apply the NPT rule on.
    type: str
    required: true
  enabled:
    description: Whether the rule is enabled.
    type: bool
    default: true
  log:
    description: Log matching packets.
    type: bool
    default: false
  description:
    description: Rule description.
    type: str
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
- name: Create an NPTv6 rule
  by_systems.opnsense.opnsense_fw_npt:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    source_net: "fd00:1::/64"
    destination_net: "2001:db8:1::/64"
    interface: wan
    description: "NPTv6 internal to external"
    state: present

- name: Idempotent check — no changes expected
  by_systems.opnsense.opnsense_fw_npt:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    source_net: "fd00:1::/64"
    destination_net: "2001:db8:1::/64"
    interface: wan
    description: "NPTv6 internal to external"
    state: present

- name: Remove an NPTv6 rule
  by_systems.opnsense.opnsense_fw_npt:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    source_net: "fd00:1::/64"
    destination_net: "2001:db8:1::/64"
    interface: wan
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
            "source_net": {"type": "str", "required": True},
            "destination_net": {"type": "str", "required": True},
            "interface": {"type": "str", "required": True},
            "enabled": {"type": "bool", "default": True},
            "log": {"type": "bool", "default": False},
            "description": {"type": "str", "default": ""},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {
        "source_net": module.params["source_net"],
        "destination_net": module.params["destination_net"],
        "interface": module.params["interface"],
        "enabled": "1" if module.params["enabled"] else "0",
        "log": "1" if module.params["log"] else "0",
    }
    if module.params["description"]:
        params["description"] = module.params["description"]

    from opnsense.managers.firewall.npt import FwNptManager

    run_module(module, FwNptManager, params)


if __name__ == "__main__":
    main()
