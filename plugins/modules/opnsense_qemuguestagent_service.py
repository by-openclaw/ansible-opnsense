#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module for the OPNsense QEMU guest agent service via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_qemuguestagent_service
short_description: Control the OPNsense QEMU guest agent service (os-qemu-guest-agent)
version_added: "0.5.0"
description:
  - Start, stop or reconfigure the QEMU guest agent service on an OPNsense firewall.
  - Thin wrapper around lib-opnsense QemuGuestAgentServiceManager.ensure().
  - >
    The service reports C(disabled) while the plugin is switched off in its
    settings (see M(by_systems.opnsense.opnsense_qemuguestagent_settings)); a C(running) request
    cannot start it in that state — enable it first.
  - C(reconfigured) always applies and is therefore never idempotent by design.
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
  state:
    description: Target service state.
    type: str
    choices: [running, stopped, reconfigured]
    default: running
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Apply changed QEMU guest agent settings
  by_systems.opnsense.opnsense_qemuguestagent_service:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    state: reconfigured
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

    from opnsense.managers.services.qemuguestagent_service import (
        QemuGuestAgentServiceManager,
    )

    run_module(module, QemuGuestAgentServiceManager, {})


if __name__ == "__main__":
    main()
