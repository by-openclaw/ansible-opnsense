#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible module: hand a fresh OPNsense box its config.xml through the boot-time importer."""

from __future__ import annotations

DOCUMENTATION = r"""
---
module: opnsense_seed_import
short_description: Seed a fresh OPNsense VM by driving its boot-time configuration importer
version_added: "0.7.0"
description:
  - >
    Boots a freshly imaged OPNsense VM on Proxmox VE and answers its configuration importer, so the
    machine comes up with the C(config.xml) carried on an attached device instead of the factory
    default. This is the only gap in an otherwise API-driven provisioning flow: a fresh appliance has
    no API, no SSH and no configuration, and the importer gates on a keypress
    (upstream C(src/sbin/opnsense-importer)).
  - >
    The module waits for the importer prompt, sends a single carriage return, answers the device
    prompt with I(device), and returns once the appliance reports that it is restoring the
    configuration. It never retries blindly and never spams the console — input sent before a prompt
    pollutes the buffer and makes the import fail.
  - >
    Idempotency - this is a one-shot action against a fresh VM, so a successful run always reports
    C(changed). Use it once per install; everything afterwards is ordinary API work.
  - Requires the C(websocket-client) Python library on the controller.
options:
  pve_host:
    description: Proxmox VE host or IP that serves the API.
    type: str
    required: true
  pve_port:
    description: Proxmox VE API port.
    type: int
    default: 8006
  pve_node:
    description: Node the VM lives on.
    type: str
    required: true
  pve_token_id:
    description: API token id, for example C(svc-terraform@pve!ci).
    type: str
    required: true
  pve_token_secret:
    description: API token secret.
    type: str
    required: true
    no_log: true
  validate_certs:
    description: Verify the Proxmox API TLS certificate.
    type: bool
    default: false
  vmid:
    description: VM id to seed.
    type: int
    required: true
  device:
    description:
      - Device name, as the appliance sees it, holding the configuration to import.
      - A second virtio-block disk is C(vtbd1); a SCSI disk would be C(da1).
    type: str
    default: vtbd1
  start_vm:
    description: Start the VM if it is not running. Set to false when something else starts it.
    type: bool
    default: true
  timeout:
    description: Seconds to wait for the import to begin before giving up.
    type: int
    default: 600
  settle:
    description: Seconds to let the import and the following boot finish before returning.
    type: int
    default: 45
author:
  - BY-SYSTEMS SRL
"""

EXAMPLES = r"""
- name: Seed a fresh firewall with the rendered config.xml on its second disk
  by_systems.opnsense.opnsense_seed_import:
    pve_host: "{{ pve_api_host }}"
    pve_node: srv-proxmox-poc-01
    pve_token_id: "{{ pve_token_id }}"
    pve_token_secret: "{{ pve_token_secret }}"
    vmid: 199
    device: vtbd1
  delegate_to: localhost
"""

RETURN = r"""
changed:
  description: True when the appliance started restoring the configuration.
  type: bool
  returned: always
imported:
  description: Whether the importer reached the restore stage.
  type: bool
  returned: always
elapsed:
  description: Seconds spent driving the console.
  type: int
  returned: always
console_tail:
  description: Last part of the console output, for diagnosis.
  type: str
  returned: always
"""

import time

from ansible.module_utils.basic import AnsibleModule

try:
    from ansible_collections.by_systems.opnsense.plugins.module_utils.pve_console import (
        HAS_WEBSOCKET,
        PveConsole,
        PveConsoleError,
        WEBSOCKET_IMPORT_ERROR,
    )
except ImportError:
    from plugins.module_utils.pve_console import (  # type: ignore
        HAS_WEBSOCKET,
        PveConsole,
        PveConsoleError,
        WEBSOCKET_IMPORT_ERROR,
    )

# What the appliance prints. Kept here so a wording change upstream is a one-line fix.
PROMPT_IMPORTER = b"configuration importer"
PROMPT_DEVICE_A = b"Select device"
PROMPT_DEVICE_B = b"leave blank"
MARK_RESTORING = b"Restoring "
MARK_NO_IMPORT = b"Default interfaces not found"


def drive(console, device, timeout, settle):
    """Answer the two prompts and wait for the restore to start.

    Returns ``(imported, elapsed, tail)``. Raises PveConsoleError on a console failure.
    """
    keyed = False
    sent = False
    buf = b""
    tail = b""
    started = time.time()

    while time.time() - started < timeout:
        chunk = console.read()
        if chunk:
            buf += chunk
            tail = (tail + chunk)[-2000:]

        if not keyed and PROMPT_IMPORTER in buf:
            console.send(b"\r")
            keyed = True
            buf = b""
            continue

        if keyed and not sent and (PROMPT_DEVICE_A in buf or PROMPT_DEVICE_B in buf):
            # a beat, so the prompt's own echo does not swallow the answer
            time.sleep(0.5)
            console.send(device + "\n")
            sent = True
            buf = b""
            continue

        if sent and MARK_RESTORING in buf:
            time.sleep(settle)
            return (
                True,
                int(time.time() - started),
                tail.decode("utf-8", errors="replace"),
            )

        if not sent and MARK_NO_IMPORT in buf:
            # the importer window closed and the appliance moved on to interface assignment
            return (
                False,
                int(time.time() - started),
                tail.decode("utf-8", errors="replace"),
            )

        if not chunk:
            time.sleep(0.1)

    return False, int(time.time() - started), tail.decode("utf-8", errors="replace")


def main() -> None:
    """Entry point for the Ansible module."""
    module = AnsibleModule(
        argument_spec={
            "pve_host": {"type": "str", "required": True},
            "pve_port": {"type": "int", "default": 8006},
            "pve_node": {"type": "str", "required": True},
            "pve_token_id": {"type": "str", "required": True},
            "pve_token_secret": {"type": "str", "required": True, "no_log": True},
            "validate_certs": {"type": "bool", "default": False},
            "vmid": {"type": "int", "required": True},
            "device": {"type": "str", "default": "vtbd1"},
            "start_vm": {"type": "bool", "default": True},
            "timeout": {"type": "int", "default": 600},
            "settle": {"type": "int", "default": 45},
        },
        supports_check_mode=True,
    )

    if not HAS_WEBSOCKET:
        module.fail_json(
            msg="the python 'websocket-client' library is required on the controller: %s"
            % WEBSOCKET_IMPORT_ERROR
        )

    p = module.params
    console = PveConsole(
        host=p["pve_host"],
        node=p["pve_node"],
        vmid=p["vmid"],
        token_id=p["pve_token_id"],
        token_secret=p["pve_token_secret"],
        validate_certs=p["validate_certs"],
        port=p["pve_port"],
    )

    try:
        state = console.status()
    except PveConsoleError as exc:
        # In check mode the VM legitimately may not exist yet — the task that creates it was itself
        # skipped. Report what would happen instead of failing the whole run.
        if module.check_mode:
            module.exit_json(
                changed=True,
                imported=False,
                elapsed=0,
                console_tail="",
                msg="would drive the importer on vmid %s once it exists, answering with device %s"
                % (p["vmid"], p["device"]),
            )
        module.fail_json(msg=str(exc))

    if module.check_mode:
        module.exit_json(
            changed=True,
            imported=False,
            elapsed=0,
            console_tail="",
            msg="would drive the importer on vmid %s (currently %s) and answer with device %s"
            % (p["vmid"], state, p["device"]),
        )

    try:
        if state != "running":
            if not p["start_vm"]:
                module.fail_json(
                    msg="vmid %s is %s and start_vm is false" % (p["vmid"], state)
                )
            console.start()
            # qemu needs a moment before the serial device accepts a session
            time.sleep(3)
        console.open()
        imported, elapsed, tail = drive(console, p["device"], p["timeout"], p["settle"])
    except PveConsoleError as exc:
        module.fail_json(msg=str(exc))
    finally:
        console.close()

    if not imported:
        module.fail_json(
            msg="the importer did not reach the restore stage within %ss — the appliance may have "
            "booted past the prompt or the device %s holds no importable configuration"
            % (p["timeout"], p["device"]),
            imported=False,
            elapsed=elapsed,
            console_tail=tail,
        )

    module.exit_json(changed=True, imported=True, elapsed=elapsed, console_tail=tail)


if __name__ == "__main__":
    main()
