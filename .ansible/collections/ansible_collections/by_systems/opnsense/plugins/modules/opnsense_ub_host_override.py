#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense Unbound host override management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ub_host_override
short_description: Manage OPNsense Unbound DNS host overrides
version_added: "0.3.0"
description:
  - Create, update, or delete Unbound DNS host overrides on OPNsense.
  - Thin wrapper around lib-opnsense UbHostOverrideManager.ensure().
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
  hostname:
    description: Hostname for the override (match key).
    type: str
    required: true
  domain:
    description: Domain for the override (match key).
    type: str
    default: ""
  server:
    description: Target IP address or hostname (match key).
    type: str
    default: ""
  rr:
    description: DNS record type.
    type: str
    choices: [A, AAAA, MX, TXT]
    default: A
  mxprio:
    description: MX priority (only for MX records).
    type: str
    default: ""
  mx:
    description: MX hostname (only for MX records).
    type: str
    default: ""
  ttl:
    description: TTL in seconds (empty for default).
    type: str
    default: ""
  txtdata:
    description: TXT record data (only for TXT records).
    type: str
    default: ""
  enabled:
    description: Whether the host override is enabled.
    type: bool
    default: true
  description:
    description: Host override description.
    type: str
    default: ""
  state:
    description: Desired state of the host override.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 1.0.0)
"""

EXAMPLES = r"""
- name: Create an A record override
  by_systems.opnsense.opnsense_ub_host_override:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    hostname: webserver
    domain: example.com
    server: "10.6.225.10"
    rr: A
    description: "Web server override"
    state: present

- name: Create a TXT record override
  by_systems.opnsense.opnsense_ub_host_override:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    hostname: _dmarc
    domain: example.com
    rr: TXT
    txtdata: "v=DMARC1; p=reject"
    state: present

- name: Remove a host override
  by_systems.opnsense.opnsense_ub_host_override:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    hostname: webserver
    domain: example.com
    server: "10.6.225.10"
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
            "hostname": {"type": "str", "required": True},
            "domain": {"type": "str", "default": ""},
            "server": {"type": "str", "default": ""},
            "rr": {
                "type": "str",
                "choices": ["A", "AAAA", "MX", "TXT"],
                "default": "A",
            },
            "mxprio": {"type": "str", "default": ""},
            "mx": {"type": "str", "default": ""},
            "ttl": {"type": "str", "default": ""},
            "txtdata": {"type": "str", "default": ""},
            "enabled": {"type": "bool", "default": True},
            "description": {"type": "str", "default": ""},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {
        "hostname": module.params["hostname"],
        "domain": module.params["domain"],
        "server": module.params["server"],
        "rr": module.params["rr"],
        "enabled": "1" if module.params["enabled"] else "0",
    }
    if module.params["mxprio"]:
        params["mxprio"] = module.params["mxprio"]
    if module.params["mx"]:
        params["mx"] = module.params["mx"]
    if module.params["ttl"]:
        params["ttl"] = module.params["ttl"]
    if module.params["txtdata"]:
        params["txtdata"] = module.params["txtdata"]
    if module.params["description"]:
        params["description"] = module.params["description"]

    from opnsense.managers.dns.ub_host_override import UbHostOverrideManager

    run_module(module, UbHostOverrideManager, params)


if __name__ == "__main__":
    main()
