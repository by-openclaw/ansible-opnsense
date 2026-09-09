#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module: render a fresh OPNsense box's config.xml from its seed profile."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_seed_config
short_description: Render the config.xml a fresh OPNsense firewall is seeded with
version_added: "0.8.0"
description:
  - >
    Renders a per-firewall C(config.xml) from a seed profile (the hardware and L2/L3 truth for one
    firewall) and a baseline XML template. The result is handed to a fresh appliance through its boot
    importer by M(by_systems.opnsense.opnsense_seed_import) — on OPNsense 26.7 the MVC API has no
    controller for interface assignment or per-interface addressing (C(interfaces/assign/*) is 404),
    so the configuration must exist before the firewall is reachable.
  - >
    The slot layout is fixed and load-bearing - C(lan) is the out-of-band port, C(opt1) the VLAN
    trunk, C(opt2..optN) the VLANs, then the WAN interfaces, then the fabric port. Firewall rules and
    VLANs in the Ansible catalog are assigned by these identifiers, so a reseed that renumbered them
    would land every rule on the wrong interface.
  - >
    Secrets (the break-glass API key and password hashes, PPPoE and static-WAN credentials, the LDAP
    bind password, the internal domain) are read from the secret store at render time and never
    committed to a seed profile. A placeholder present in the template with no secret behind it is an
    error, so a firewall is never seeded with an empty admin credential.
  - >
    Idempotency - the rendered configuration is compared with what is already at I(dest), ignoring
    the freshly salted genesis hashes, which differ on every render by design.
options:
  seed:
    description: Parsed seed profile for this firewall. Mutually exclusive with I(seed_file).
    type: dict
  seed_file:
    description: Path to the seed profile JSON. Mutually exclusive with I(seed).
    type: path
  baseline:
    description: Path to the baseline C(config.xml) template holding the secret placeholders.
    type: path
    required: true
  dest:
    description: Where to write the rendered C(config.xml).
    type: path
    required: true
  secret_dir:
    description: Directory holding the fabric secret files the placeholders are filled from.
    type: path
    required: true
  bcrypt_rounds:
    description: Cost factor for the genesis GUI password hash.
    type: int
    default: 10
requirements:
  - bcrypt
  - passlib (only on Python 3.13+, where the stdlib C(crypt) module was removed)
author:
  - BY-SYSTEMS Platform Team (@by-openclaw)
"""

EXAMPLES = r"""
- name: Render the seed configuration for a firewall
  by_systems.opnsense.opnsense_seed_config:
    seed_file: "{{ seed_dir }}/seeds/vm-opns-01.json"
    baseline: "{{ seed_dir }}/templates/baseline.xml"
    dest: "{{ seed_dir }}/out/vm-opns-01/conf/config.xml"
    secret_dir: "~/.openclaw/workspace/infra/secrets/fabric"
  no_log: true
"""

RETURN = r"""
path:
  description: Path the configuration was written to.
  type: str
  returned: always
hostname:
  description: Hostname the configuration was rendered for.
  type: str
  returned: always
slots:
  description: Logical role to OPNsense interface identifier mapping the render produced.
  type: dict
  returned: always
"""

import json
import os
import re

from ansible.module_utils.basic import AnsibleModule

try:  # collection path when installed, repo path when tested
    from ansible_collections.by_systems.opnsense.plugins.module_utils.seed_config import (
        SeedConfigError,
        compute_slot_map,
        redact,
        render_config,
    )
except ImportError:  # pragma: no cover - repo-local import for unit tests
    from plugins.module_utils.seed_config import (  # type: ignore
        SeedConfigError,
        compute_slot_map,
        redact,
        render_config,
    )

# The genesis hashes carry a fresh salt on every render, so they can never match what is
# already on disk. Blank them on both sides before deciding whether anything changed.
_VOLATILE = (
    re.compile(r"(<apikeys>.*?</apikeys>)", re.DOTALL),
    re.compile(r"(<password>\$2[aby]\$.*?</password>)", re.DOTALL),
)


def _stable(text: str) -> str:
    for pattern in _VOLATILE:
        text = pattern.sub("<volatile/>", text)
    return text


def main() -> None:
    module = AnsibleModule(
        argument_spec={
            "seed": {"type": "dict"},
            "seed_file": {"type": "path"},
            "baseline": {"type": "path", "required": True},
            "dest": {"type": "path", "required": True},
            "secret_dir": {"type": "path", "required": True},
            "bcrypt_rounds": {"type": "int", "default": 10},
        },
        mutually_exclusive=[["seed", "seed_file"]],
        required_one_of=[["seed", "seed_file"]],
        supports_check_mode=True,
    )

    seed = module.params["seed"]
    try:
        if seed is None:
            with open(module.params["seed_file"], "r", encoding="utf-8") as handle:
                seed = json.load(handle)
        with open(module.params["baseline"], "r", encoding="utf-8") as handle:
            baseline = handle.read()
        rendered = render_config(
            seed,
            baseline,
            module.params["secret_dir"],
            bcrypt_rounds=module.params["bcrypt_rounds"],
        )
        slots = compute_slot_map(seed)
    except (OSError, ValueError) as exc:
        module.fail_json(
            msg="cannot read the seed profile or baseline template: %s" % exc
        )
    except SeedConfigError as exc:
        module.fail_json(msg=str(exc))

    dest = module.params["dest"]
    before = ""
    if os.path.exists(dest):
        try:
            with open(dest, "r", encoding="utf-8") as handle:
                before = handle.read()
        except OSError as exc:
            module.fail_json(
                msg="cannot read the existing configuration at %s: %s" % (dest, exc)
            )

    changed = _stable(before) != _stable(rendered)
    if changed and not module.check_mode:
        try:
            parent = os.path.dirname(dest)
            if parent and not os.path.isdir(parent):
                os.makedirs(parent, mode=0o700)
            with open(dest, "w", encoding="utf-8") as handle:
                handle.write(rendered)
            os.chmod(dest, 0o600)
        except OSError as exc:
            module.fail_json(
                msg="cannot write the configuration to %s: %s" % (dest, exc)
            )

    module.exit_json(
        changed=changed,
        path=dest,
        hostname=seed.get("hostname", ""),
        slots=slots,
        diff={"before": redact(before), "after": redact(rendered)},
    )


if __name__ == "__main__":
    main()
