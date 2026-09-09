#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_plugin — thin wrapper on lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_plugin
short_description: Install or remove an OPNsense plugin (os-*) and wait for the firmware job
version_added: "0.5.0"
description:
  - >
    Idempotent plugin install/remove through the firmware job API (lib-opnsense PluginManager.ensure()).
  - >
    The backend reports the job as done even when it REFUSED it (a fresh 26.7.0 image: "Installation out of date. The update to opnsense-26.7.3_11 is required."; an unknown package name) — the verdict is read from the job log and surfaced as a failure with the reason.
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
    description: Plugin package name (e.g. C(os-chrony)).
    type: str
    required: true
  wait:
    description: Wait for the firmware job to finish and verify the result.
    type: bool
    default: true
  timeout:
    description: Seconds to wait for the firmware job.
    type: int
    default: 300
  state:
    description: C(present) installs, C(absent) removes.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Ensure os-chrony is installed
  by_systems.opnsense.opnsense_plugin:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: os-chrony
"""

RETURN = r"""
changed:
  description: Whether state on the firewall was modified.
  type: bool
  returned: always
action:
  description: One of C(installed), C(removed) or C(noop).
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


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update(
        {
            "name": {"type": "str", "required": True},
            "wait": {"type": "bool", "default": True},
            "timeout": {"type": "int", "default": 300},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    from opnsense.managers.services.plugin import PluginManager

    run_module(
        module,
        PluginManager,
        {},
        ensure_kwargs={
            "package_name": module.params["name"],
            "wait": module.params["wait"],
            "timeout": module.params["timeout"],
        },
    )


if __name__ == "__main__":
    main()
