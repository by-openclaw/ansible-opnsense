#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module for the OPNsense NetFlow / Insight settings via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_netflow_settings
short_description: Manage the OPNsense NetFlow / Insight capture and collection settings
version_added: "0.8.0"
description:
  - Declare which interfaces are captured, the export version and targets, and whether the local Insight collector runs.
  - Thin wrapper around lib-opnsense NetflowSettingsManager.ensure() (C(diagnostics/netflow/getconfig), C(setconfig), C(reconfigure)).
  - Only the options you set are diffed and sent — everything else is left untouched. Interface lists are compared as sets.
  - Requires OPNsense >= 26.7.5 (C(setconfig) did not save on earlier firmware, which is why the seed used to carry this block).
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
      - Off by default — deleting is never a silent default. Not used by this singleton.
    type: bool
    default: false
  interfaces:
    description: Interface identifiers to capture flows on (C(lan), C(opt1), …).
    type: list
    elements: str
  egress_only:
    description: Interfaces captured on egress only — the uplinks, so a flow is not counted twice.
    type: list
    elements: str
  version:
    description: NetFlow export version.
    type: str
    choices: [v5, v9]
  targets:
    description: Export targets as C(address:port). The local Insight collector listens on C(127.0.0.1:2056).
    type: list
    elements: str
  collect:
    description: Run the local Insight collector (API field C(collect.enable)).
    type: bool
  active_timeout:
    description: Seconds after which an active flow is exported (API field C(activeTimeout)).
    type: str
  inactive_timeout:
    description: Seconds after which an idle flow is exported (API field C(inactiveTimeout)).
    type: str
  state:
    description: Only C(present) is supported (singleton settings).
    type: str
    choices: [present]
    default: present
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Capture every internal interface, uplinks on egress only, local Insight collector
  by_systems.opnsense.opnsense_netflow_settings:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    interfaces: [lan, opt1, opt2, opt12]
    egress_only: [opt12]
    version: v9
    targets: ["127.0.0.1:2056"]
    collect: true
"""

RETURN = r"""
changed:
  description: Whether any setting drifted.
  type: bool
  returned: always
action:
  description: One of C(updated) or C(noop).
  type: str
  returned: always
diff:
  description: Before/after settings.
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

# Options of the nested `capture` block. Multi-selects: the manager normalises a list to
# the CSV the API expects and compares the selection as a set.
_CAPTURE_LIST_FIELDS = ("interfaces", "egress_only", "targets")
# Module option -> top-level API field.
_TIMEOUT_FIELDS = {"active_timeout": "activeTimeout", "inactive_timeout": "inactiveTimeout"}


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update({f: {"type": "list", "elements": "str"} for f in _CAPTURE_LIST_FIELDS})
    spec.update(
        {
            "version": {"type": "str", "choices": ["v5", "v9"]},
            "collect": {"type": "bool"},
            "active_timeout": {"type": "str"},
            "inactive_timeout": {"type": "str"},
            "state": {"type": "str", "choices": ["present"], "default": "present"},
        }
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    # Only send what the caller actually set: the manager diffs solely the keys it
    # receives, so an unset option leaves that setting untouched.
    capture: dict = {}
    for field in _CAPTURE_LIST_FIELDS:
        if module.params.get(field) is not None:
            capture[field] = list(module.params[field])
    if module.params.get("version") is not None:
        capture["version"] = module.params["version"]

    params: dict = {}
    if capture:
        params["capture"] = capture
    if module.params.get("collect") is not None:
        params["collect"] = {"enable": "1" if module.params["collect"] else "0"}
    for option, api_field in _TIMEOUT_FIELDS.items():
        if module.params.get(option) is not None:
            params[api_field] = module.params[option]

    from opnsense.managers.services.netflow_settings import NetflowSettingsManager

    run_module(module, NetflowSettingsManager, params)


if __name__ == "__main__":
    main()
