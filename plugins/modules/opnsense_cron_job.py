#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense cron job management via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_cron_job
short_description: Manage OPNsense cron jobs
version_added: "0.3.0"
description:
  - Create, update, or delete cron jobs on OPNsense.
  - Thin wrapper around lib-opnsense CronJobManager.ensure().
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
    description: Cron job description (unique identifier / match key).
    type: str
    required: true
  enabled:
    description: Whether the cron job is enabled.
    type: bool
    default: true
  minutes:
    description: Minutes field (cron syntax).
    type: str
    default: "0"
  hours:
    description: Hours field (cron syntax).
    type: str
    default: "0"
  days:
    description: Day of month field (cron syntax).
    type: str
    default: "*"
  months:
    description: Month field (cron syntax).
    type: str
    default: "*"
  weekdays:
    description: Day of week field (cron syntax).
    type: str
    default: "*"
  command:
    description: OPNsense command to execute.
    type: str
    default: ""
  who:
    description: User to execute the command as.
    type: str
    default: root
  parameters:
    description: Additional command parameters.
    type: str
    default: ""
  state:
    description: Desired state of the cron job.
    type: str
    choices: [present, absent]
    default: present
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 1.0.0)
"""

EXAMPLES = r"""
- name: Create a daily firmware check cron job
  by_systems.opnsense.opnsense_cron_job:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Daily firmware update check"
    minutes: "0"
    hours: "3"
    command: "firmware auto-update"
    state: present

- name: Create a weekly config backup
  by_systems.opnsense.opnsense_cron_job:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Weekly config backup"
    minutes: "30"
    hours: "2"
    weekdays: "0"
    command: "system backups"
    state: present

- name: Remove a cron job
  by_systems.opnsense.opnsense_cron_job:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Old cron job"
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
            "minutes": {"type": "str", "default": "0"},
            "hours": {"type": "str", "default": "0"},
            "days": {"type": "str", "default": "*"},
            "months": {"type": "str", "default": "*"},
            "weekdays": {"type": "str", "default": "*"},
            "command": {"type": "str", "default": ""},
            "who": {"type": "str", "default": "root"},
            "parameters": {"type": "str", "default": ""},
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
        "minutes": module.params["minutes"],
        "hours": module.params["hours"],
        "days": module.params["days"],
        "months": module.params["months"],
        "weekdays": module.params["weekdays"],
        "who": module.params["who"],
    }
    if module.params["command"]:
        params["command"] = module.params["command"]
    if module.params["parameters"]:
        params["parameters"] = module.params["parameters"]

    from opnsense.managers.services.cron_job import CronJobManager

    run_module(module, CronJobManager, params)


if __name__ == "__main__":
    main()
