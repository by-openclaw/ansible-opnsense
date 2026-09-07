#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_mdnsrepeater_settings — thin wrapper on lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_mdnsrepeater_settings
short_description: Manage OPNsense mDNS repeater (os-mdns-repeater) settings
version_added: "0.5.0"
description:
  - Manage the os-mdns-repeater plugin settings — lib-opnsense MdnsRepeaterSettingsManager.ensure().
  - Repeats mDNS (Bonjour/Avahi) between at least two I(interfaces).
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
    description: Enable the repeater.
    type: bool
  interfaces:
    description: Interface slot ids to repeat between (>= 2).
    type: list
    elements: str
  blocklist:
    description: Networks whose announcements are dropped.
    type: list
    elements: str
  enablecarp:
    description: Follow CARP master state.
    type: bool
  state:
    description: Only C(present) is supported (singleton settings).
    type: str
    choices: [present]
    default: present
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Repeat mDNS between MGMT, media and gaming
  by_systems.opnsense.opnsense_mdnsrepeater_settings:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    enabled: true
    interfaces: [opt2, opt8, opt10]
"""

RETURN = r"""
changed:
  description: Whether state on the firewall was modified.
  type: bool
  returned: always
action:
  description: One of C(updated) or C(noop).
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


_BOOL_FIELDS = ("enabled", "enablecarp")
_STR_FIELDS = ()
_LIST_FIELDS = ("interfaces", "blocklist")
_ENUMS = {}
_API_NAMES = {}


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update({f: {"type": "bool"} for f in _BOOL_FIELDS})
    spec.update(
        {
            f: {"type": "str", **({"choices": _ENUMS[f]} if f in _ENUMS else {})}
            for f in _STR_FIELDS
        }
    )
    spec.update({f: {"type": "list", "elements": "str"} for f in _LIST_FIELDS})
    spec.update(
        {"state": {"type": "str", "choices": ["present"], "default": "present"}}
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

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

    from opnsense.managers.services.mdnsrepeater_settings import (
        MdnsRepeaterSettingsManager,
    )

    run_module(module, MdnsRepeaterSettingsManager, params)


if __name__ == "__main__":
    main()
