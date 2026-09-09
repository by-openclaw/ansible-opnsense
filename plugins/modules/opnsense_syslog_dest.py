#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense syslog destination management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_syslog_dest
short_description: Manage OPNsense syslog destinations
version_added: "0.3.0"
description:
  - Create, update, or delete syslog remote destinations on OPNsense.
  - Thin wrapper around lib-opnsense SyslogDestManager.ensure().
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
  description:
    description: Syslog destination description (unique identifier / match key).
    type: str
    required: true
  enabled:
    description: Whether the syslog destination is enabled.
    type: bool
    default: true
  transport:
    description: Transport protocol for syslog delivery.
    type: str
    choices: [udp4, tcp4, udp6, tcp6, tls4, tls6]
    default: udp4
  hostname:
    description: Remote syslog server hostname or IP address.
    type: str
    required: true
  syslog_port:
    description: Remote syslog server port.
    type: str
    default: "514"
  rfc5424:
    description: Use RFC 5424 syslog format (instead of BSD/RFC 3164).
    type: bool
    default: false
  certificate:
    description: TLS certificate UUID for encrypted transport.
    type: str
    default: ""
  state:
    description: Desired state of the syslog destination.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 1.0.0)
"""

EXAMPLES = r"""
- name: Create a syslog destination for Loki
  by_systems.opnsense.opnsense_syslog_dest:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Loki syslog ingester"
    transport: tcp4
    hostname: "10.6.225.20"
    syslog_port: "1514"
    rfc5424: true
    state: present

- name: Create a UDP syslog destination
  by_systems.opnsense.opnsense_syslog_dest:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Central syslog"
    hostname: "10.6.225.21"
    state: present

- name: Remove a syslog destination
  by_systems.opnsense.opnsense_syslog_dest:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Old syslog"
    hostname: "10.6.225.99"
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
            "description": {"type": "str", "required": True},
            "enabled": {"type": "bool", "default": True},
            "transport": {
                "type": "str",
                "choices": ["udp4", "tcp4", "udp6", "tcp6", "tls4", "tls6"],
                "default": "udp4",
            },
            "hostname": {"type": "str", "required": True},
            "syslog_port": {"type": "str", "default": "514"},
            "rfc5424": {"type": "bool", "default": False},
            "certificate": {"type": "str", "default": ""},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {
        "description": module.params["description"],
        "enabled": "1" if module.params["enabled"] else "0",
        "transport": module.params["transport"],
        "hostname": module.params["hostname"],
        "port": module.params["syslog_port"],
        "rfc5424": "1" if module.params["rfc5424"] else "0",
    }
    if module.params["certificate"]:
        params["certificate"] = module.params["certificate"]

    from opnsense.managers.services.syslog_dest import SyslogDestManager

    run_module(module, SyslogDestManager, params)


if __name__ == "__main__":
    main()
