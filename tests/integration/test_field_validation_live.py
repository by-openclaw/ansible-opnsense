# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Integration tests — field validation with invalid inputs against a live OPNsense device.

Requirements:
    - Live OPNsense device accessible via OPN_HOST, OPN_KEY, OPN_SECRET env vars
    - API user must have full admin privileges
    - Run with: pytest tests/integration/test_field_validation_live.py -v

Test flow (ordered):
    1. Bad enum: filter action       — invalid action value raises FieldValidationError
    2. Bad enum: filter direction    — invalid direction value raises FieldValidationError
    3. Bad enum: filter ipprotocol   — invalid ipprotocol value raises FieldValidationError
    4. Bad enum: VIP mode            — invalid mode value raises FieldValidationError
    5. Bad bool: filter enabled      — 'yes' instead of '0'/'1' raises FieldValidationError
    6. Bad int: VLAN tag zero        — tag=0 raises FieldValidationError
    7. Bad int: VLAN tag above max   — tag=5000 raises FieldValidationError
    8. Bad int: VLAN tag non-numeric — tag='abc' raises FieldValidationError
    9. Bad IP: malformed address     — '999.999.999.999' raises FieldValidationError
    10. Bad IP: IPv6 in Kea4 field   — server rejects IPv6 with OpnsenseValidationError
    11. Bad IP: not an IP            — 'not-an-ip' raises FieldValidationError
    12. Bad MAC: invalid hex chars   — 'XX:YY:ZZ:...' raises FieldValidationError
    13. Bad MAC: too short           — '00:11:22' raises FieldValidationError
    14. Required: empty user name    — empty string raises FieldValidationError
    15. Required: empty alias name   — empty string raises FieldValidationError
    16. Required: empty group name   — empty string raises FieldValidationError
    17. Bad state param              — invalid state raises ValueError

Naming convention:
    All test objects use prefix 'inttest-' to avoid collision with real config.
"""
from __future__ import annotations

import pytest

from opnsense.exceptions import FieldValidationError, OpnsenseValidationError
from opnsense.managers.auth.group import AuthGroupManager
from opnsense.managers.auth.user import AuthUserManager
from opnsense.managers.dhcp.kea4_reservation import Kea4ReservationManager
from opnsense.managers.firewall.alias import FwAliasManager
from opnsense.managers.firewall.filter import FwFilterManager
from opnsense.managers.interfaces.vip import IfVipManager
from opnsense.managers.interfaces.vlan import IfVlanManager

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


class TestBadEnumValues:
    """Wrong enum value → FieldValidationError (client-side)."""

    async def test_filter_bad_action(self, opn_client):
        mgr = FwFilterManager(opn_client)
        with pytest.raises(FieldValidationError, match="action"):
            await mgr.ensure("present", {
                "description": "inttest-bad-enum",
                "action": "INVALID_ACTION",
                "interface": "lan",
                "direction": "in",
                "protocol": "TCP",
                "enabled": "0",
            })

    async def test_filter_bad_direction(self, opn_client):
        mgr = FwFilterManager(opn_client)
        with pytest.raises(FieldValidationError, match="direction"):
            await mgr.ensure("present", {
                "description": "inttest-bad-direction",
                "action": "pass",
                "interface": "lan",
                "direction": "sideways",
                "protocol": "TCP",
                "enabled": "0",
            })

    async def test_filter_bad_ipprotocol(self, opn_client):
        mgr = FwFilterManager(opn_client)
        with pytest.raises(FieldValidationError, match="ipprotocol"):
            await mgr.ensure("present", {
                "description": "inttest-bad-ipproto",
                "action": "pass",
                "interface": "lan",
                "direction": "in",
                "ipprotocol": "ipv99",
                "protocol": "TCP",
                "enabled": "0",
            })

    async def test_vip_bad_mode(self, opn_client):
        mgr = IfVipManager(opn_client)
        with pytest.raises(FieldValidationError, match="mode"):
            await mgr.ensure("present", {
                "address": "10.11.99.99/32",
                "interface": "lan",
                "mode": "invalid_mode",
                "network": "10.11.99.99/32",
            })


class TestBadBoolStrValues:
    """Bool fields must be '0' or '1' — not true/false/yes/no."""

    async def test_filter_bad_enabled(self, opn_client):
        mgr = FwFilterManager(opn_client)
        with pytest.raises(FieldValidationError, match="enabled"):
            await mgr.ensure("present", {
                "description": "inttest-bad-bool",
                "action": "pass",
                "interface": "lan",
                "direction": "in",
                "protocol": "TCP",
                "enabled": "yes",
            })


class TestBadIntValues:
    """Integer fields: out of range, non-numeric."""

    async def test_vlan_tag_zero(self, opn_client):
        mgr = IfVlanManager(opn_client)
        with pytest.raises(FieldValidationError, match="tag"):
            await mgr.ensure("present", {"tag": "0", "if": "vtnet0"})

    async def test_vlan_tag_above_max(self, opn_client):
        mgr = IfVlanManager(opn_client)
        with pytest.raises(FieldValidationError, match="tag"):
            await mgr.ensure("present", {"tag": "5000", "if": "vtnet0"})

    async def test_vlan_tag_non_numeric(self, opn_client):
        mgr = IfVlanManager(opn_client)
        with pytest.raises(FieldValidationError, match="tag"):
            await mgr.ensure("present", {"tag": "abc", "if": "vtnet0"})


class TestBadIpAddresses:
    """IP address validation — malformed, wrong class, etc."""

    async def test_kea4_reservation_bad_ip(self, opn_client):
        mgr = Kea4ReservationManager(opn_client)
        with pytest.raises(FieldValidationError, match="ip_address"):
            await mgr.ensure("present", {
                "ip_address": "999.999.999.999",
                "hw_address": "00:11:22:33:44:55",
            })

    async def test_kea4_reservation_ipv6_in_v4(self, opn_client):
        """IPv6 address passes client-side ip validator (accepts both v4/v6)
        but server rejects it because Kea4 only accepts IPv4."""
        mgr = Kea4ReservationManager(opn_client)
        with pytest.raises(OpnsenseValidationError, match="ip_address"):
            await mgr.ensure("present", {
                "ip_address": "fd99::1",
                "hw_address": "00:11:22:33:44:55",
            })

    async def test_kea4_reservation_not_ip(self, opn_client):
        mgr = Kea4ReservationManager(opn_client)
        with pytest.raises(FieldValidationError, match="ip_address"):
            await mgr.ensure("present", {
                "ip_address": "not-an-ip",
                "hw_address": "00:11:22:33:44:55",
            })


class TestBadMacAddresses:
    """MAC address validation."""

    async def test_kea4_reservation_bad_mac(self, opn_client):
        mgr = Kea4ReservationManager(opn_client)
        with pytest.raises(FieldValidationError, match="hw_address"):
            await mgr.ensure("present", {
                "ip_address": "10.99.0.50",
                "hw_address": "XX:YY:ZZ:11:22:33",
            })

    async def test_kea4_reservation_short_mac(self, opn_client):
        mgr = Kea4ReservationManager(opn_client)
        with pytest.raises(FieldValidationError, match="hw_address"):
            await mgr.ensure("present", {
                "ip_address": "10.99.0.50",
                "hw_address": "00:11:22",
            })


class TestRequiredFieldMissing:
    """Required fields that are empty or absent."""

    async def test_user_empty_name(self, opn_client):
        mgr = AuthUserManager(opn_client)
        with pytest.raises(FieldValidationError, match="name"):
            await mgr.ensure("present", {"name": ""})

    async def test_alias_empty_name(self, opn_client):
        mgr = FwAliasManager(opn_client)
        with pytest.raises(FieldValidationError, match="name"):
            await mgr.ensure("present", {"name": ""})

    async def test_group_empty_name(self, opn_client):
        mgr = AuthGroupManager(opn_client)
        with pytest.raises(FieldValidationError, match="name"):
            await mgr.ensure("present", {"name": ""})


class TestBadStateParam:
    """ensure() with invalid state."""

    async def test_invalid_state(self, opn_client):
        mgr = FwFilterManager(opn_client)
        with pytest.raises(ValueError, match="state"):
            await mgr.ensure("invalid", {
                "description": "inttest-bad-state",
                "action": "pass",
                "interface": "lan",
                "direction": "in",
                "protocol": "TCP",
            })
