#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module for the OPNsense ACME client service (os-acme-client) via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_acme_service
short_description: Control the OPNsense ACME client service (os-acme-client)
version_added: "0.6.0"
description:
  - Start, stop or reconfigure the ACME client service on an OPNsense firewall.
  - Thin wrapper around lib-opnsense AcmeServiceManager.ensure().
  - C(reconfigured) regenerates the acme.sh configuration and the renewal cron; it always applies and is therefore never idempotent by design.
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
- name: Apply changed ACME settings/objects (regenerate acme.sh config + cron)
  by_systems.opnsense.opnsense_acme_service:
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

    from opnsense.managers.acme.service import AcmeServiceManager

    run_module(module, AcmeServiceManager, {})


if __name__ == "__main__":
    main()
