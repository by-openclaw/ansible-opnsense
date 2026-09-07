#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module for OPNsense os-qemu-guest-agent general settings via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_qemuguestagent_settings
short_description: Manage OPNsense QEMU guest agent (os-qemu-guest-agent) settings
version_added: "0.5.0"
description:
  - Manage the os-qemu-guest-agent plugin settings (Proxmox/KVM guest integration).
  - Thin wrapper around lib-opnsense QemuGuestAgentSettingsManager.ensure().
  - API field names are CamelCase; this module exposes snake_case.
  - Only the options you set are diffed and sent — everything else is left untouched.
  - Requires OPNsense >= 26.1 and the os-qemu-guest-agent plugin.
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
    description: Enable the guest agent.
    type: bool
  log_debug:
    description: Debug logging.
    type: bool
  disabled_rpcs:
    description: guest-* RPC names to block (e.g. guest-exec).
    type: list
    elements: str
  state:
    description: Only C(present) is supported (singleton settings).
    type: str
    choices: [present]
    default: present
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Manage OPNsense QEMU guest agent (os-qemu-guest-agent) settings
  by_systems.opnsense.opnsense_qemuguestagent_settings:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    enabled: true
    disabled_rpcs: [guest-exec, guest-exec-status]
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
_BOOL_FIELDS = ("enabled", "log_debug")
_STR_FIELDS = ()
# Multi-selects: the manager normalises a list to the CSV the API expects.
_LIST_FIELDS = ("disabled_rpcs",)
# Module option -> API field (only where they differ).
_API_NAMES = {
    "enabled": "Enabled",
    "log_debug": "LogDebug",
    "disabled_rpcs": "DisabledRPCs",
}


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

    from opnsense.managers.services.qemuguestagent_settings import (
        QemuGuestAgentSettingsManager,
    )

    run_module(module, QemuGuestAgentSettingsManager, params)


if __name__ == "__main__":
    main()
