#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_ids_settings — thin wrapper on lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ids_settings
short_description: Manage OPNsense Intrusion Detection (Suricata) general settings
version_added: "0.5.0"
description:
  - >
    Manage the C(general) block of the built-in Suricata IDS/IPS — lib-opnsense IdsSettingsManager.ensure().
  - >
    I(mode) C(pcap) = IDS (alert only); C(netmap)/C(divert) = inline IPS. A seeded firewall stores the OPNsense default I(interfaces)=wan, which is not a valid slot on our seeds — set I(interfaces) here BEFORE toggling rulesets, or every IDS save fails validation.
  - Only the options you set are diffed and sent.
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
    description: Enable Suricata.
    type: bool
  mode:
    description: pcap (IDS), netmap or divert (IPS).
    type: str
    choices: ['pcap', 'netmap', 'divert']
  interfaces:
    description: Interface slot ids to inspect.
    type: list
    elements: str
  homenet:
    description: HOME_NET networks.
    type: list
    elements: str
  promisc:
    description: Promiscuous mode.
    type: bool
  syslog:
    description: Alerts to syslog.
    type: bool
  syslog_eve:
    description: EVE JSON to syslog (the Loki path).
    type: bool
  log_payload:
    description: Log packet payloads (API field C(LogPayload)).
    type: bool
  eve_log:
    description: EVE log types to enable (http, tls) — API field C(eveLog).
    type: list
    elements: str
  alert_logrotate:
    description: Alert log rotation (API C(AlertLogrotate)).
    type: str
    choices: ['D0', 'W0D23']
  alert_save_logs:
    description: Alert logs to keep (API C(AlertSaveLogs)).
    type: str
  mpm_algo:
    description: Pattern matcher (API C(MPMAlgo)).
    type: str
    choices: ['', 'ac', 'ac-ks', 'hs']
  verbosity:
    description: Log verbosity.
    type: str
    choices: ['', 'v', 'vv', 'vvv', 'vvvv']
  default_packet_size:
    description: Default packet size (API C(defaultPacketSize)).
    type: str
  divert_listeners:
    description: Divert listeners.
    type: bool
  detect_profile:
    description: Detection-engine profile (nested API block C(detect.Profile)); empty = OPNsense default.
    type: str
    choices: ["", low, medium, high, custom]
  state:
    description: Only C(present) is supported (singleton settings).
    type: str
    choices: [present]
    default: present
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Alert-only IDS on the Proximus WAN
  by_systems.opnsense.opnsense_ids_settings:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    enabled: true
    mode: pcap
    interfaces: [opt12]
    homenet: ["10.1.0.0/16", "fd01::/32"]
    syslog_eve: true
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


_BOOL_FIELDS = (
    "enabled",
    "promisc",
    "syslog",
    "syslog_eve",
    "log_payload",
    "divert_listeners",
)
_STR_FIELDS = (
    "mode",
    "alert_logrotate",
    "alert_save_logs",
    "mpm_algo",
    "verbosity",
    "default_packet_size",
)
_LIST_FIELDS = ("interfaces", "homenet", "eve_log")
_ENUMS = {
    "mode": ["pcap", "netmap", "divert"],
    "alert_logrotate": ["D0", "W0D23"],
    "mpm_algo": ["", "ac", "ac-ks", "hs"],
    "verbosity": ["", "v", "vv", "vvv", "vvvv"],
}
_API_NAMES = {
    "log_payload": "LogPayload",
    "eve_log": "eveLog",
    "alert_logrotate": "AlertLogrotate",
    "alert_save_logs": "AlertSaveLogs",
    "mpm_algo": "MPMAlgo",
    "default_packet_size": "defaultPacketSize",
}


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
        {
            "detect_profile": {
                "type": "str",
                "choices": ["", "low", "medium", "high", "custom"],
            }
        }
    )
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

    if module.params.get("detect_profile") is not None:
        params["detect"] = {"Profile": module.params["detect_profile"]}

    from opnsense.managers.ids.settings import IdsSettingsManager

    run_module(module, IdsSettingsManager, params)


if __name__ == "__main__":
    main()
