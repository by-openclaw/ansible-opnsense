#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense CrowdSec plugin settings via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_crowdsec_settings
short_description: Manage OPNsense CrowdSec (os-crowdsec) plugin settings
version_added: "0.3.0"
description:
  - Manage the os-crowdsec plugin configuration on an OPNsense firewall.
  - Thin wrapper around lib-opnsense CrowdSecSettingsManager.ensure().
  - >
    A default install enables the plugin's own LAPI on 127.0.0.1 and points the
    firewall bouncer at it. The firewall then reports healthy while being
    isolated from a central LAPI, so decisions raised elsewhere are never
    enforced. Set I(lapi_manual_configuration) to point the bouncer at a remote
    LAPI instead.
  - Requires OPNsense >= 26.1 and the os-crowdsec plugin.
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
  agent_enabled:
    description: Run the local log-processing agent on the firewall.
    type: bool
  lapi_enabled:
    description: Run a Local API on the firewall itself.
    type: bool
  firewall_bouncer_enabled:
    description: Run the firewall bouncer, which enforces decisions in pf.
    type: bool
  lapi_manual_configuration:
    description:
      - Configure the LAPI connection manually rather than using the local one.
      - Required when the bouncer must pull from a remote LAPI.
    type: bool
  lapi_listen_address:
    description: Address the local LAPI binds to, when it is enabled.
    type: str
  lapi_listen_port:
    description: Port the local LAPI binds to, when it is enabled.
    type: str
  rules_enabled:
    description: Insert the CrowdSec block rules into the ruleset.
    type: bool
  rules_log:
    description: Log packets dropped by the CrowdSec rules.
    type: bool
  rules_tag:
    description:
      - Optional tag applied to the generated rules.
      - Alphanumeric only, 1-63 characters — the API rejects hyphens.
    type: str
  crowdsec_firewall_verbose:
    description: Verbose logging for the firewall bouncer.
    type: bool
  state:
    description: Only C(present) is meaningful for a settings singleton.
    type: str
    choices: [present]
    default: present
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Firewall acts as a bouncer only, pulling from the central LAPI
  by_systems.opnsense.opnsense_crowdsec_settings:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    agent_enabled: false
    lapi_enabled: false
    firewall_bouncer_enabled: true
    lapi_manual_configuration: true
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
  description: Before/after settings, with enroll_key redacted.
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

# API booleans are the strings "0"/"1", not JSON booleans.
_BOOL_FIELDS = (
    "agent_enabled",
    "lapi_enabled",
    "firewall_bouncer_enabled",
    "lapi_manual_configuration",
    "rules_enabled",
    "rules_log",
    "crowdsec_firewall_verbose",
)
_STR_FIELDS = ("lapi_listen_address", "lapi_listen_port", "rules_tag")


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update({f: {"type": "bool"} for f in _BOOL_FIELDS})
    spec.update({f: {"type": "str"} for f in _STR_FIELDS})
    spec.update(
        {"state": {"type": "str", "choices": ["present"], "default": "present"}}
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    # Only send what the caller actually set: the manager diffs solely the keys
    # it receives, so an unset option leaves that setting untouched.
    params: dict = {}
    for field in _BOOL_FIELDS:
        if module.params.get(field) is not None:
            params[field] = "1" if module.params[field] else "0"
    for field in _STR_FIELDS:
        if module.params.get(field) is not None:
            params[field] = module.params[field]

    from opnsense.managers.crowdsec.settings import CrowdSecSettingsManager

    run_module(module, CrowdSecSettingsManager, params)


if __name__ == "__main__":
    main()
