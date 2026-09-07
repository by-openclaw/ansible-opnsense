#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module for the OPNsense Unbound service via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ub_service
short_description: Control the OPNsense Unbound resolver service
version_added: "0.5.0"
description:
  - Start, stop or reconfigure the Unbound DNS resolver on an OPNsense firewall.
  - Thin wrapper around lib-opnsense UbServiceManager.ensure().
  - >
    The service reports C(disabled) while the resolver is switched off in its
    general settings (see M(by_systems.opnsense.opnsense_ub_settings)); a
    C(running) request cannot start it in that state — enable it first.
  - C(reconfigured) always applies (re-reads forwards, overrides, ACLs) and is
    therefore never idempotent by design.
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
  state:
    description: Target service state.
    type: str
    choices: [running, stopped, reconfigured]
    default: running
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Apply changed forwards / overrides
  by_systems.opnsense.opnsense_ub_service:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    state: reconfigured

- name: Make sure the resolver is up
  by_systems.opnsense.opnsense_ub_service:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    state: running
"""

RETURN = r"""
changed:
  description: Whether the service state was modified.
  type: bool
  returned: always
action:
  description: One of C(started), C(stopped), C(restarted), C(reconfigured) or C(noop).
  type: str
  returned: always
diff:
  description: Before/after C(status).
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
            "state": {
                "type": "str",
                "choices": ["running", "stopped", "reconfigured"],
                "default": "running",
            }
        }
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    from opnsense.managers.dns.ub_service import UbServiceManager

    run_module(module, UbServiceManager, {})


if __name__ == "__main__":
    main()
