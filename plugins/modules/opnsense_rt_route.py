#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense static route management."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_rt_route
short_description: Manage OPNsense static routes
version_added: "0.2.0"
description:
  - Create, update, or delete static routes on OPNsense.
  - Thin wrapper around lib-opnsense RtRouteManager.ensure().
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
    description: OPNsense API port.
    type: int
    default: 443
  verify_ssl:
    description: Verify SSL certificate.
    type: bool
    default: false
  network:
    description: Destination network in CIDR notation (match key).
    type: str
    required: true
  gateway:
    description: Gateway name (match key). Use 'Null4' or 'Null6' for blackhole routes.
    type: str
    required: true
  descr:
    description: Route description.
    type: str
    default: ""
  disabled:
    description: Disable this route.
    type: bool
    default: false
  state:
    description: Desired state of the route.
    type: str
    choices: [present, absent]
    default: present
requirements:
  - lib-opnsense >= 1.0.0
author:
  - BY-SYSTEMS (@by-openclaw)
"""

EXAMPLES = r"""
- name: Create blackhole route (disabled for testing)
  by_systems.opnsense.opnsense_rt_route:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    network: 10.99.0.0/24
    gateway: Null4
    descr: inttest-blackhole-route
    disabled: true
    state: present

- name: Delete route
  by_systems.opnsense.opnsense_rt_route:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    network: 10.99.0.0/24
    gateway: Null4
    state: absent
"""

RETURN = r"""
changed:
  description: Whether the resource was changed.
  type: bool
  returned: always
action:
  description: Action taken (created, updated, deleted, noop).
  type: str
  returned: always
uuid:
  description: UUID of the resource.
  type: str
  returned: when available
diff:
  description: Before/after state when changed.
  type: dict
  returned: when changed
"""

try:
    from ansible_collections.by_systems.opnsense.plugins.module_utils.opnsense_helper import (
        opn_argument_spec,
        run_module,
    )
except ImportError:
    from plugins.module_utils.opnsense_helper import opn_argument_spec, run_module

from ansible.module_utils.basic import AnsibleModule


def main() -> None:
    spec = opn_argument_spec()
    spec.update(
        {
            "network": {"type": "str", "required": True},
            "gateway": {"type": "str", "required": True},
            "descr": {"type": "str", "default": ""},
            "disabled": {"type": "bool", "default": False},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    params: dict = {
        "network": module.params["network"],
        "gateway": module.params["gateway"],
        "disabled": "1" if module.params["disabled"] else "0",
    }
    if module.params["descr"]:
        params["descr"] = module.params["descr"]

    from opnsense.managers.routing.route import RtRouteManager

    run_module(module, RtRouteManager, params)


if __name__ == "__main__":
    main()
