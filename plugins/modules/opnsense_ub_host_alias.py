#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense Unbound host alias management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ub_host_alias
short_description: Manage OPNsense Unbound DNS host aliases
version_added: "0.3.0"
description:
  - Create, update, or delete Unbound DNS host aliases on OPNsense.
  - Thin wrapper around lib-opnsense UbHostAliasManager.ensure().
  - "NOTE: create/read only on OPNsense 26.1.5 — update/delete may not be available."
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
    description: Alias hostname (match key).
    type: str
    required: true
  domain:
    description: Alias domain (match key).
    type: str
    default: ""
  host_uuid:
    description: UUID of the parent host override this alias belongs to.
    type: str
    default: ""
  enabled:
    description: Whether the host alias is enabled.
    type: bool
    default: true
  description:
    description: Host alias description.
    type: str
    default: ""
  state:
    description: Desired state of the host alias.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 1.0.0)
"""

EXAMPLES = r"""
- name: Create a host alias
  by_systems.opnsense.opnsense_ub_host_alias:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    hostname: www
    domain: example.com
    host_uuid: "{{ parent_override_uuid }}"
    description: "Alias for webserver"
    state: present

- name: Remove a host alias
  by_systems.opnsense.opnsense_ub_host_alias:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    hostname: www
    domain: example.com
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
            "host_uuid": {"type": "str", "default": ""},
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
        "enabled": "1" if module.params["enabled"] else "0",
    }
    if module.params["host_uuid"]:
        params["host"] = module.params["host_uuid"]
    if module.params["description"]:
        params["description"] = module.params["description"]

    from opnsense.managers.dns.ub_host_alias import UbHostAliasManager

    run_module(module, UbHostAliasManager, params)


if __name__ == "__main__":
    main()
