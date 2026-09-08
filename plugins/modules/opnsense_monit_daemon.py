#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module for the OPNsense Monit daemon (os-monit) via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_monit_daemon
short_description: Control the OPNsense Monit daemon (os-monit)
version_added: "0.6.0"
description:
  - Start, stop or reconfigure the Monit daemon on an OPNsense firewall.
  - Thin wrapper around lib-opnsense MonitDaemonManager.ensure().
  - >
    This drives the daemon itself; the monitored-service entries are
    M(by_systems.opnsense.opnsense_monit_service), the SMTP/general block is
    M(by_systems.opnsense.opnsense_monit_settings).
  - >
    C(reconfigured) regenerates monitrc, runs the syntax test and (re)starts the daemon.
    A refused config is answered with HTTP 200 C(status failed) by the plugin — the module
    fails with the plugin's message instead of leaving Monit down. It always applies and is
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
- name: Ensure the Monit daemon is running (after settings/alerts/checks converged)
  by_systems.opnsense.opnsense_monit_daemon:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    state: running

- name: Regenerate monitrc and restart Monit (fails loudly on a refused config)
  by_systems.opnsense.opnsense_monit_daemon:
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

    from opnsense.managers.monit.daemon import MonitDaemonManager

    run_module(module, MonitDaemonManager, {})


if __name__ == "__main__":
    main()
