#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module opnsense_monit_settings — thin wrapper on lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_monit_settings
short_description: Manage OPNsense Monit general settings (SMTP alerting, HTTP interface, M/Monit)
version_added: "0.5.0"
description:
  - Manage the C(general) block of Monit — lib-opnsense MonitSettingsManager.ensure().
  - Only the options you set are diffed and sent — everything else is left untouched.
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
  enabled:
    description: Enable Monit.
    type: bool
  interval:
    description: Poll interval (s).
    type: str
  startdelay:
    description: Start delay (s).
    type: str
  mailserver:
    description: SMTP server.
    type: str
  smtp_port:
    description: SMTP port (API field C(port)).
    type: str
  username:
    description: SMTP username.
    type: str
  password:
    description: SMTP password.
    type: str
    no_log: true
  ssl:
    description: Use SSL/STARTTLS.
    type: bool
  sslversion:
    description: TLS version (AUTO, TLSV1, TLSV11, TLSV12, TLSV13).
    type: str
  sslverify:
    description: Verify the SMTP certificate.
    type: bool
  httpd_enabled:
    description: Enable the Monit HTTP interface.
    type: bool
  httpd_port:
    description: HTTP interface port.
    type: str
  httpd_username:
    description: HTTP interface username.
    type: str
  httpd_password:
    description: HTTP interface password.
    type: str
    no_log: true
  httpd_allow:
    description: HTTP interface allow list.
    type: str
  mmonit_url:
    description: M/Monit URL.
    type: str
    no_log: true
  mmonit_timeout:
    description: M/Monit timeout (s).
    type: str
  mmonit_register_credentials:
    description: Register credentials with M/Monit.
    type: bool
  logfile:
    description: Log file.
    type: str
  statefile:
    description: State file.
    type: str
  eventqueue_path:
    description: Event queue path.
    type: str
  eventqueue_slots:
    description: Event queue slots.
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
- name: Monit alerts through our mail relay
  by_systems.opnsense.opnsense_monit_settings:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    enabled: true
    mailserver: "{{ smtp_host }}"
    smtp_port: "587"
    username: "{{ smtp_user }}"
    password: "{{ smtp_pass }}"
    ssl: true
    sslverify: true
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
    "ssl",
    "sslverify",
    "httpd_enabled",
    "mmonit_register_credentials",
)
_STR_FIELDS = (
    "interval",
    "startdelay",
    "mailserver",
    "smtp_port",
    "username",
    "password",
    "sslversion",
    "httpd_port",
    "httpd_username",
    "httpd_password",
    "httpd_allow",
    "mmonit_url",
    "mmonit_timeout",
    "logfile",
    "statefile",
    "eventqueue_path",
    "eventqueue_slots",
)
_API_NAMES = {
    "smtp_port": "port",
    "httpd_enabled": "httpdEnabled",
    "httpd_port": "httpdPort",
    "httpd_username": "httpdUsername",
    "httpd_password": "httpdPassword",  # pragma: allowlist secret (field NAMES only)
    "httpd_allow": "httpdAllow",
    "mmonit_url": "mmonitUrl",
    "mmonit_timeout": "mmonitTimeout",
    "mmonit_register_credentials": "mmonitRegisterCredentials",
    "eventqueue_path": "eventqueuePath",
    "eventqueue_slots": "eventqueueSlots",
}


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update({f: {"type": "bool"} for f in _BOOL_FIELDS})
    spec.update(
        {
            f: {
                "type": "str",
                "no_log": f
                in (
                    "httpd_password",
                    "mmonit_url",
                    "password",
                ),  # pragma: allowlist secret (field NAMES, not values)
            }
            for f in _STR_FIELDS
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

    from opnsense.managers.monit.settings import MonitSettingsManager

    run_module(module, MonitSettingsManager, params)


if __name__ == "__main__":
    main()
