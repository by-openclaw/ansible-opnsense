#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense GIF tunnel interface management."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_if_gif
short_description: Manage OPNsense GIF tunnel interfaces
version_added: "0.2.0"
description:
  - Create, update, or delete GIF (Generic Tunnel Interface) on OPNsense.
  - Thin wrapper around lib-opnsense IfGifManager.ensure().
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
  tunnel_local_addr:
    description: >
      Local tunnel endpoint address (used as match key).
      Maps to "tunnel-local-addr" in the OPNsense API.
    type: str
    required: true
  tunnel_remote_addr:
    description: >
      Remote tunnel endpoint address (used as match key).
      Maps to "tunnel-remote-addr" in the OPNsense API.
    type: str
    required: true
  descr:
    description: GIF tunnel description.
    type: str
    default: ""
  state:
    description: Desired state of the GIF tunnel.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 0.1.0)
"""

EXAMPLES = r"""
- name: Create a GIF tunnel
  by_systems.opnsense.opnsense_if_gif:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    tunnel_local_addr: "198.51.100.1"
    tunnel_remote_addr: "203.0.113.1"
    descr: "GIF tunnel to remote site"
    state: present

- name: Idempotent check — no changes expected
  by_systems.opnsense.opnsense_if_gif:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    tunnel_local_addr: "198.51.100.1"
    tunnel_remote_addr: "203.0.113.1"
    descr: "GIF tunnel to remote site"
    state: present

- name: Remove a GIF tunnel
  by_systems.opnsense.opnsense_if_gif:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    tunnel_local_addr: "198.51.100.1"
    tunnel_remote_addr: "203.0.113.1"
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
            "tunnel_local_addr": {"type": "str", "required": True},
            "tunnel_remote_addr": {"type": "str", "required": True},
            "descr": {"type": "str", "default": ""},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {
        "tunnel-local-addr": module.params["tunnel_local_addr"],
        "tunnel-remote-addr": module.params["tunnel_remote_addr"],
    }
    if module.params["descr"]:
        params["descr"] = module.params["descr"]

    from opnsense.managers.interfaces.gif import IfGifManager

    run_module(module, IfGifManager, params)


if __name__ == "__main__":
    main()
