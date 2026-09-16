# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Unit tests for the console conversation in opnsense_seed_import.drive().

No Proxmox, no VM: a fake console replays what the appliance prints and records what we send, so
the ordering rules are pinned — one carriage return at the importer prompt, the device only after
its own prompt, and nothing at all before either. Sending early pollutes the appliance's input
buffer and the import fails, which is why the ordering is worth a test.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from plugins.modules.opnsense_seed_import import drive  # noqa: E402


class FakeConsole:
    """Replays chunks the appliance would print; records everything written back."""

    def __init__(self, chunks):
        self._chunks = list(chunks)
        self.sent = []

    def read(self):
        return self._chunks.pop(0) if self._chunks else b""

    def send(self, data):
        self.sent.append(data if isinstance(data, bytes) else data.encode())


BOOT = b"OPNsense 26.7 booting\n"
IMPORTER = b"Press any key to start the configuration importer: ......\n"
DEVICE = b"Select device to import from (e.g. ada0) or leave blank to exit: "
RESTORE = b"Restoring config.xml...\n"


def test_answers_both_prompts_in_order():
    c = FakeConsole([BOOT, IMPORTER, DEVICE, RESTORE])
    imported, elapsed, tail = drive(c, "vtbd1", timeout=5, settle=0)
    assert imported is True
    assert c.sent == [b"\r", b"vtbd1\n"]
    assert "Restoring" in tail
    assert elapsed >= 0


def test_sends_nothing_before_the_importer_prompt():
    c = FakeConsole([BOOT, BOOT, BOOT])
    imported, _, _ = drive(c, "vtbd1", timeout=1, settle=0)
    assert imported is False
    assert c.sent == []


def test_device_is_not_sent_before_its_prompt():
    c = FakeConsole([IMPORTER, BOOT, BOOT])
    imported, _, _ = drive(c, "vtbd1", timeout=1, settle=0)
    assert imported is False
    assert c.sent == [b"\r"]


def test_gives_up_when_the_appliance_boots_past_the_window():
    c = FakeConsole([BOOT, b"Default interfaces not found, running assignment\n"])
    imported, _, tail = drive(c, "vtbd1", timeout=5, settle=0)
    assert imported is False
    assert "Default interfaces not found" in tail
    assert c.sent == []


def test_honours_a_non_default_device_name():
    c = FakeConsole([IMPORTER, DEVICE, RESTORE])
    imported, _, _ = drive(c, "da1", timeout=5, settle=0)
    assert imported is True
    assert c.sent == [b"\r", b"da1\n"]


def test_times_out_without_the_restore_marker():
    c = FakeConsole([IMPORTER, DEVICE])
    imported, elapsed, _ = drive(c, "vtbd1", timeout=1, settle=0)
    assert imported is False
    assert elapsed >= 1


@pytest.mark.parametrize(
    "prompt", [b"Select device to import from", b"or leave blank to exit"]
)
def test_accepts_either_half_of_the_device_prompt(prompt):
    c = FakeConsole([IMPORTER, prompt, RESTORE])
    imported, _, _ = drive(c, "vtbd1", timeout=5, settle=0)
    assert imported is True
    assert c.sent == [b"\r", b"vtbd1\n"]
