#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_core_service — thin wrapper on lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_core_service
short_description: Start / stop / restart a registered OPNsense daemon by name (core/service)
version_added: "0.5.0"
description:
  - >
    Drives the generic service registry used by legacy daemons without an MVC controller (C(ntpd), C(syslog-ng), C(openssh), …) — lib-opnsense CoreServiceManager.ensure().
  - >
    An unregistered daemon counts as stopped: C(stopped) is a noop, C(running) attempts a start. C(restarted) always fires.
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
  name:
    description: Service id as listed by C(core/service/search) (e.g. C(ntpd)).
    type: str
    required: true
  state:
    description: Target state.
    type: str
    choices: [running, stopped, restarted]
    default: running
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: chrony owns :123 now — keep the legacy ntpd down
  by_systems.opnsense.opnsense_core_service:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: ntpd
    state: stopped
"""

RETURN = r"""
changed:
  description: Whether state on the firewall was modified.
  type: bool
  returned: always
action:
  description: One of C(started), C(stopped), C(restarted) or C(noop).
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
            "state": {
                "type": "str",
                "choices": ["running", "stopped", "restarted"],
                "default": "running",
            },
        }
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    from opnsense.managers.services.core_service import CoreServiceManager

    run_module(
        module, CoreServiceManager, {}, ensure_kwargs={"name": module.params["name"]}
    )


if __name__ == "__main__":
    main()
