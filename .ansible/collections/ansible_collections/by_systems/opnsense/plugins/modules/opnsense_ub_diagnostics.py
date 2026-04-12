#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense

"""Ansible module for OPNsense Unbound diagnostics info via lib-opnsense."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_ub_diagnostics
short_description: Retrieve OPNsense Unbound DNS diagnostics
version_added: "0.3.0"
description:
  - Retrieve Unbound DNS statistics or DNSBL information from OPNsense.
  - This is an info module — it never changes state.
  - Thin wrapper around lib-opnsense UbDiagnosticsManager.
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
  info_type:
    description: Type of diagnostic information to retrieve.
    type: str
    required: true
    choices: [stats, dnsbl]
author:
  - BY-SYSTEMS (@by-openclaw)
requirements:
  - opnsense (lib-opnsense >= 1.0.0)
"""

EXAMPLES = r"""
- name: Get Unbound statistics
  by_systems.opnsense.opnsense_ub_diagnostics:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    info_type: stats
  register: dns_stats

- name: Get DNSBL information
  by_systems.opnsense.opnsense_ub_diagnostics:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    info_type: dnsbl
  register: dnsbl_info

- name: Display DNS cache hit ratio
  debug:
    msg: "DNS stats: {{ dns_stats.data }}"
"""

RETURN = r"""
changed:
  description: Always false — this is an info module.
  type: bool
  returned: always
data:
  description: Dictionary with diagnostic data (stats or dnsbl).
  type: dict
  returned: always
"""

import asyncio

from ansible.module_utils.basic import AnsibleModule

try:
    from ansible_collections.by_systems.opnsense.plugins.module_utils.opnsense_helper import (
        _handle_opnsense_error,
        opn_argument_spec,
    )
except ImportError:
    from plugins.module_utils.opnsense_helper import _handle_opnsense_error, opn_argument_spec


async def _run(module: AnsibleModule) -> dict:
    """Execute diagnostics query with try/except/finally."""
    from opnsense.client import OpnsenseClient
    from opnsense.managers.dns.ub_diagnostics import UbDiagnosticsManager

    client = None
    try:
        client = OpnsenseClient(
            host=module.params["host"],
            key=module.params["key"],
            secret=module.params["secret"],
            port=module.params["port"],
            verify_ssl=module.params["verify_ssl"],
        )
        await client.__aenter__()

        mgr = UbDiagnosticsManager(client)
        info_type = module.params["info_type"]

        if info_type == "stats":
            data = await mgr.get_stats()
        else:
            data = await mgr.get_dnsbl()

        return {
            "changed": False,
            "data": data,
        }

    except ImportError as exc:
        module.fail_json(
            msg="lib-opnsense is required. Install with: pip install opnsense",
            exception=str(exc),
        )
    except Exception as exc:
        _handle_opnsense_error(module, exc)
    finally:
        if client is not None:
            await client.close()

    return {}


def main() -> None:
    """Entry point for the Ansible module."""
    spec = opn_argument_spec()
    spec.update(
        {
            "info_type": {
                "type": "str",
                "required": True,
                "choices": ["stats", "dnsbl"],
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    result = asyncio.run(_run(module))
    module.exit_json(**result)


if __name__ == "__main__":
    main()
