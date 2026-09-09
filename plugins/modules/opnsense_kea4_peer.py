#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense Kea DHCPv4 HA peer management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_kea4_peer
short_description: Manage OPNsense Kea DHCPv4 HA peers
version_added: "0.3.0"
description:
  - Create, update, or delete Kea DHCPv4 high-availability peers on OPNsense.
  - Thin wrapper around lib-opnsense Kea4PeerManager.ensure().
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
  name:
    description: Peer name (unique identifier / match key).
    type: str
    required: true
  role:
    description: HA role for this peer.
    type: str
    choices: [primary, standby]
    default: primary
  url:
    description: Peer URL for HA communication.
    type: str
    required: true
  state:
    description: Desired state of the peer.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 1.0.0)
"""

EXAMPLES = r"""
- name: Add a standby HA peer
  by_systems.opnsense.opnsense_kea4_peer:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: fw-standby
    role: standby
    url: "http://10.6.225.2:8000/"
    state: present

- name: Remove an HA peer
  by_systems.opnsense.opnsense_kea4_peer:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: fw-standby
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
            "name": {"type": "str", "required": True},
            "role": {
                "type": "str",
                "choices": ["primary", "standby"],
                "default": "primary",
            },
            "url": {"type": "str", "required": True},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {
        "name": module.params["name"],
        "role": module.params["role"],
        "url": module.params["url"],
    }

    from opnsense.managers.dhcp.kea4_peer import Kea4PeerManager

    run_module(module, Kea4PeerManager, params)


if __name__ == "__main__":
    main()
