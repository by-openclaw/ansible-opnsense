# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Integration tests — duplicate detection for firewall rules against a live OPNsense device.

Requirements:
    - Live OPNsense device accessible via OPN_HOST, OPN_KEY, OPN_SECRET env vars
    - API user must have full admin privileges
    - Run with: pytest tests/integration/test_duplicate_detection.py -v

Test flow (ordered):
    1. Create duplicates           — create two identical disabled FW rules via direct create
    2. Ensure raises ambiguous     — ensure() on duplicate pair raises AmbiguousMatchError
    3. Full cleanup                — delete all inttest-ansible-dup filter rules

Naming convention:
    All test objects use prefix 'inttest-ansible-dup' to avoid collision with real config.
"""
from __future__ import annotations

import pytest

from opnsense.exceptions import AmbiguousMatchError
from opnsense.managers.firewall.filter import FwFilterManager

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

DUP_PARAMS = {
    "description": "inttest-ansible-dup",
    "action": "pass",
    "interface": "lan",
    "direction": "in",
    "protocol": "TCP",
    "destination_port": "443",
    "enabled": "0",
}


class TestAnsibleDuplicateDetection:
    """Verify AmbiguousMatchError propagates correctly."""

    async def test_01_create_duplicates(self, opn_client):
        mgr = FwFilterManager(opn_client)
        r1 = await mgr.create(params=DUP_PARAMS)
        r2 = await mgr.create(params=DUP_PARAMS)
        assert r1.uuid != r2.uuid

    async def test_02_ensure_raises_ambiguous(self, opn_client):
        mgr = FwFilterManager(opn_client)
        with pytest.raises(AmbiguousMatchError) as exc_info:
            await mgr.ensure(state="present", params=DUP_PARAMS)
        assert len(exc_info.value.uuids) >= 2

    async def test_03_cleanup(self, opn_client):
        mgr = FwFilterManager(opn_client)
        rows = await mgr.list(search_phrase="inttest-ansible-dup")
        for r in rows:
            if r.get("description") == "inttest-ansible-dup":
                await mgr.delete(uuid=r["uuid"])
