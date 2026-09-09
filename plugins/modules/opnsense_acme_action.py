#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_acme_action — thin wrapper on lib-opnsense (AcmeActionManager)."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_acme_action
short_description: Manage OPNsense ACME post-issue automations (actions)
version_added: "0.6.0"
description:
  - CRUD for ACME automations (matched by I(name)) — lib-opnsense AcmeActionManager.ensure().
  - I(type=configd_restart_gui) restarts the WebGUI after a certificate update.
  - Requires the C(os-acme-client) plugin.
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
    description: Action name (match key).
    type: str
    required: true
  description:
    description: Free-text description.
    type: str
  type:
    description: Action type (e.g. C(configd_restart_gui), C(configd_restart_haproxy), C(configd_generic), C(configd_upload_sftp), C(configd_remote_ssh)).
    type: str
  enabled:
    description: Enable the action.
    type: bool
  configd_generic_command:
    description: configd command (I(type=configd_generic)).
    type: str
  sftp_host:
    description: SFTP upload host.
    type: str
  sftp_host_key:
    description: SFTP known-host key.
    type: str
  sftp_port:
    description: SFTP port.
    type: str
  sftp_user:
    description: SFTP username.
    type: str
  sftp_identity_type:
    description: SFTP key type.
    type: str
    choices: [ecdsa, rsa, ed25519]
  sftp_remote_path:
    description: Remote directory for uploads.
    type: str
  remote_ssh_host:
    description: Remote SSH host.
    type: str
  remote_ssh_host_key:
    description: Remote SSH known-host key.
    type: str
  remote_ssh_port:
    description: Remote SSH port.
    type: str
  remote_ssh_user:
    description: Remote SSH username.
    type: str
  remote_ssh_identity_type:
    description: Remote SSH key type.
    type: str
    choices: [ecdsa, rsa, ed25519]
  remote_ssh_command:
    description: Command to run over SSH.
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
- name: Restart the WebGUI after a certificate update
  by_systems.opnsense.opnsense_acme_action:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: restart-webgui
    type: configd_restart_gui
"""

RETURN = r"""
changed:
  description: Whether the resource was modified.
  type: bool
  returned: always
action:
  description: What happened (C(created), C(updated), C(deleted), C(noop)).
  type: str
  returned: always
uuid:
  description: UUID of the affected resource.
  type: str
  returned: when present
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


_BOOL_FIELDS = ('enabled',)
_STR_FIELDS = ('name', 'description', 'type', 'configd_generic_command', 'sftp_host', 'sftp_host_key', 'sftp_port', 'sftp_user', 'sftp_identity_type', 'sftp_remote_path', 'remote_ssh_host', 'remote_ssh_host_key', 'remote_ssh_port', 'remote_ssh_user', 'remote_ssh_identity_type', 'remote_ssh_command')
_ENUMS = {'sftp_identity_type': ['ecdsa', 'rsa', 'ed25519'], 'remote_ssh_identity_type': ['ecdsa', 'rsa', 'ed25519']}
_REQUIRED = ('name',)
_NO_LOG = ('sftp_host_key', 'remote_ssh_host_key')  # pragma: allowlist secret (field NAMES, not values)


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update({f: {"type": "bool"} for f in _BOOL_FIELDS})
    spec.update(
        {
            f: {
                "type": "str",
                "required": f in _REQUIRED,
                "no_log": f in _NO_LOG,
                **({"choices": _ENUMS[f]} if f in _ENUMS else {}),
            }
            for f in _STR_FIELDS
        }
    )
    spec.update({"state": {"type": "str", "choices": ['present', 'absent'], "default": "present"}})
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    # Match key always; other options only when set, so an unset option leaves that
    # field untouched on an existing entry (same contract as the other CRUD modules).
    params: dict = {}
    for field in _BOOL_FIELDS:
        if module.params.get(field) is not None:
            params[field] = "1" if module.params[field] else "0"
    for field in _STR_FIELDS:
        if module.params.get(field) is not None:
            params[field] = module.params[field]

    from opnsense.managers.acme.actions import AcmeActionManager

    run_module(module, AcmeActionManager, params)


if __name__ == "__main__":
    main()
