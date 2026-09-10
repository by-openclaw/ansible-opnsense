# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Unit tests for the seed config.xml renderer.

The slot layout these tests pin is load-bearing: the Ansible catalog assigns every firewall rule and
VLAN by interface identifier, so a render that numbered the WANs before the VLANs would put every
rule on the wrong interface after a reseed. The fixtures use documentation addresses only — no real
firewall identity, no real secrets.
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from plugins.module_utils.seed_config import (  # noqa: E402
    SeedConfigError,
    build_netflow,
    compute_slot_map,
    redact,
    render_config,
)

FIXTURES = Path(__file__).parent / "fixtures" / "seed"
BASELINE = (FIXTURES / "baseline.xml").read_text()
HASHES = {"api": "$6$fixedsalt$apihash", "webgui": "$2b$10$fixedsaltfixedsaltfixedsalt"}


@pytest.fixture()
def secret_dir(tmp_path: Path) -> Path:
    """A throwaway secret store holding exactly what the fixtures reference."""
    (tmp_path / "OPNsense.seed-bootstrap.json").write_text(
        json.dumps(
            {"fields": {"root_password_hash": "$2b$10$root"}}
        )  # pragma: allowlist secret
    )
    (tmp_path / "genesis.json").write_text(
        json.dumps(
            {
                "fields": {
                    "key": "fixturekey",
                    "secret": "fixturesecret",  # pragma: allowlist secret
                    "webgui_password": "fixturepw",  # pragma: allowlist secret
                }
            }
        )
    )
    (tmp_path / "pppoe-fixture.json").write_text(
        json.dumps(
            {
                "fields": {
                    "pppoe_username": "user@isp",
                    "pppoe_password": "pppoepw",  # pragma: allowlist secret
                }
            }
        )
    )
    (tmp_path / "wan2-fixture.json").write_text(
        json.dumps(
            {
                "fields": {
                    "ipv4_address": "198.51.100.10",
                    "ipv4_prefix": 29,
                    "ipv4_gateway": "198.51.100.9",
                    "ipv6_address": "2001:db8:ffff::10",
                    "ipv6_prefix": 64,
                    "ipv6_gateway": "2001:db8:ffff::1",
                }
            }
        )
    )
    return tmp_path


def _seed(name: str, secret_dir: Path) -> dict:
    text = (
        (FIXTURES / f"{name}.json")
        .read_text()
        .replace("__SECRET_DIR__", str(secret_dir))
    )
    return json.loads(text)


def _render(name: str, secret_dir: Path) -> ET.Element:
    return ET.fromstring(
        render_config(
            _seed(name, secret_dir), BASELINE, str(secret_dir), genesis_hashes=HASHES
        )
    )


def test_slot_layout_puts_vlans_before_the_wans(secret_dir: Path) -> None:
    slots = compute_slot_map(_seed("full", secret_dir))
    assert slots == {
        "lan": "lan",
        "trunk": "opt1",
        "vlan0.100": "opt2",
        "vlan0.200": "opt3",
        "wan": "opt4",
        "wan2": "opt5",
        "fab": "opt6",
    }


def test_minimal_seed_renders_oob_trunk_and_loopback_only(secret_dir: Path) -> None:
    ifs = _render("minimal", secret_dir).find("interfaces")
    assert [child.tag for child in ifs] == ["lan", "opt1", "lo0"]
    assert ifs.find("lan/ipaddr").text == "dhcp"
    assert ifs.find("lan/subnet") is None  # dhcp carries no prefix


def test_an_oob_only_firewall_gets_a_default_route_from_its_seed(
    secret_dir: Path,
) -> None:
    seed = _seed("minimal", secret_dir)
    seed["lan"] = {
        "if": "vtnet1",
        "descr": "OOB",
        "ipv4": "192.0.2.197",
        "ipv4_prefix": 24,
        "ipv4_gateway": "192.0.2.1",
    }
    root = ET.fromstring(
        render_config(seed, BASELINE, str(secret_dir), genesis_hashes=HASHES)
    )
    assert root.find("interfaces/lan/gateway").text == "OOB_GW"
    item = root.find("gateways/gateway_item")
    assert item.find("interface").text == "lan"
    assert item.find("gateway").text == "192.0.2.1"
    assert item.find("defaultgw").text == "1"  # nothing else can be the default here


def test_the_oob_gateway_never_takes_the_default_from_a_wan(secret_dir: Path) -> None:
    seed = _seed("full", secret_dir)
    seed["lan"]["ipv4"] = "192.0.2.195"
    seed["lan"]["ipv4_prefix"] = 24
    seed["lan"]["ipv4_gateway"] = "192.0.2.1"
    root = ET.fromstring(
        render_config(seed, BASELINE, str(secret_dir), genesis_hashes=HASHES)
    )
    oob = [g for g in root.find("gateways") if g.find("name").text == "OOB_GW"][0]
    assert oob.find("defaultgw") is None
    assert oob.find("monitor_disable").text == "1"


def test_a_dhcp_oob_port_gets_no_static_gateway(secret_dir: Path) -> None:
    root = _render("minimal", secret_dir)  # the fixture's OOB port is dhcp
    assert root.find("interfaces/lan/gateway") is None


def test_minimal_seed_emits_no_gateways_and_no_ppps(secret_dir: Path) -> None:
    root = _render("minimal", secret_dir)
    assert root.find("gateways") is None
    assert root.find("ppps") is None
    assert root.find("vlans") is not None and len(root.find("vlans")) == 0


def test_full_seed_places_each_interface_on_its_slot(secret_dir: Path) -> None:
    ifs = _render("full", secret_dir).find("interfaces")
    assert ifs.find("opt2/if").text == "vlan0.100"
    assert ifs.find("opt4/if").text == "pppoe0"  # WAN after the VLANs
    assert ifs.find("opt5/if").text == "vtnet3"
    assert ifs.find("opt6/if").text == "vtnet4"  # fabric last
    assert ifs.find("opt6/subnet").text == "20"


def test_prefix_delegation_tracking_wins_over_the_static_address(
    secret_dir: Path,
) -> None:
    ifs = _render("full", secret_dir).find("interfaces")
    assert ifs.find("opt2/ipaddrv6").text == "track6"
    assert ifs.find("opt2/track6-interface").text == "opt12"
    assert ifs.find("opt2/track6-prefix-id").text == "0x1"
    assert ifs.find("opt2/subnetv6") is None
    # the VLAN with no tracking entry keeps its static address
    assert ifs.find("opt3/ipaddrv6").text == "2001:db8:0:200::1"
    assert (
        ifs.find("opt3/subnet").text == "26"
    )  # per-VLAN prefix beats the seed default


def test_pppoe_wan_carries_the_isp_quirks(secret_dir: Path) -> None:
    wan = _render("full", secret_dir).find("interfaces/opt4")
    assert wan.find("dhcp6prefixonly").text == "1"
    assert wan.find("dhcp6-ia-pd-len").text == "8"  # /56 hint on the 0-based scale
    assert wan.find("dhcp6-rapid-commit").text == "1"
    assert wan.find("blockpriv").text == "1"
    assert wan.find("blockbogons").text == "1"


def test_static_wan_gets_both_gateways_from_the_secret(secret_dir: Path) -> None:
    gws = _render("full", secret_dir).find("gateways")
    names = [g.find("name").text for g in gws]
    assert names == ["WAN_TELENET_GW", "WAN_TELENET_GWv6"]
    assert gws[0].find("interface").text == "opt5"
    assert gws[0].find("gateway").text == "198.51.100.9"
    assert gws[0].find("defaultgw").text == "1"
    assert gws[1].find("ipprotocol").text == "inet6"
    assert gws[1].find("defaultgw") is None  # only v4 is declared default


def test_pppoe_credentials_come_from_the_secret_store(secret_dir: Path) -> None:
    ppp = _render("full", secret_dir).find("ppps/ppp")
    assert ppp.find("ports").text == "vtnet2"
    assert ppp.find("username").text == "user@isp"
    assert ppp.find("mtu").text == "1492"


def test_netflow_captures_every_slot_except_the_fabric(secret_dir: Path) -> None:
    slots = compute_slot_map(_seed("full", secret_dir))
    capture = build_netflow(slots).find("Netflow/capture")
    assert capture.find("interfaces").text == "lan,opt1,opt2,opt3,opt4,opt5"
    assert capture.find("egress_only").text == "opt4,opt5"


def test_ipv6_is_explicitly_allowed(secret_dir: Path) -> None:
    settings = _render("minimal", secret_dir).find("OPNsense/Interfaces/settings")
    assert settings.find("disableipv6").text == "0"
    assert settings.find("disablechecksumoffloading").text == "1"


def test_identity_comes_from_the_seed(secret_dir: Path) -> None:
    system = _render("full", secret_dir).find("system")
    assert system.find("hostname").text == "vm-opns-fixture-full"
    assert system.find("domain").text == "example.invalid"
    assert system.find("timezone").text == "Etc/UTC"


def test_render_is_reproducible_for_the_same_inputs(secret_dir: Path) -> None:
    seed = _seed("full", secret_dir)
    first = render_config(seed, BASELINE, str(secret_dir), genesis_hashes=HASHES)
    second = render_config(seed, BASELINE, str(secret_dir), genesis_hashes=HASHES)
    assert first == second


def test_a_placeholder_with_no_secret_behind_it_fails(secret_dir: Path) -> None:
    (secret_dir / "OPNsense.seed-bootstrap.json").write_text(json.dumps({"fields": {}}))
    with pytest.raises(SeedConfigError, match="root_password_hash"):
        render_config(
            _seed("minimal", secret_dir),
            BASELINE,
            str(secret_dir),
            genesis_hashes=HASHES,
        )


def test_a_seed_without_genesis_credentials_fails(secret_dir: Path) -> None:
    seed = _seed("minimal", secret_dir)
    del seed["genesis_creds_file"]
    with pytest.raises(SeedConfigError, match="genesis_creds_file"):
        render_config(seed, BASELINE, str(secret_dir), genesis_hashes=HASHES)


def test_a_missing_secret_file_names_itself(secret_dir: Path) -> None:
    (secret_dir / "genesis.json").unlink()
    with pytest.raises(SeedConfigError, match="genesis secret file not found"):
        render_config(
            _seed("minimal", secret_dir),
            BASELINE,
            str(secret_dir),
            genesis_hashes=HASHES,
        )


def test_static_wan_without_its_secret_reference_fails(secret_dir: Path) -> None:
    seed = _seed("full", secret_dir)
    del seed["wan2"]["creds_secret"]
    with pytest.raises(SeedConfigError, match="creds_secret"):
        render_config(seed, BASELINE, str(secret_dir), genesis_hashes=HASHES)


def test_redaction_blanks_every_injected_secret() -> None:
    rendered = redact(
        "\n".join(
            [
                "  <password>$2b$10$averyrealhash</password>",
                "  <apikeys>key|$6$salt$hash</apikeys>",
                "  <authorizedkeys>c3NoLWVkMjU1MTk=</authorizedkeys>",
                "  <hostname>vm-opns-01</hostname>",
            ]
        )
    )
    assert "$2b$10$averyrealhash" not in rendered
    assert "$6$salt$hash" not in rendered
    assert "c3NoLWVkMjU1MTk=" not in rendered
    assert "<hostname>vm-opns-01</hostname>" in rendered


def test_a_seed_can_name_its_own_resolvers(secret_dir: Path) -> None:
    # The baseline's public resolver is unreachable on a management segment that blocks
    # external DNS, and a firewall that cannot resolve cannot reach the firmware mirrors.
    seed = _seed("minimal", secret_dir)
    seed["dns_servers"] = ["10.6.224.1", "10.1.3.101"]
    root = ET.fromstring(
        render_config(seed, BASELINE, str(secret_dir), genesis_hashes=HASHES)
    )
    assert [e.text for e in root.find("system").findall("dnsserver")] == [
        "10.6.224.1",
        "10.1.3.101",
    ]


def test_a_seed_without_resolvers_keeps_the_baseline(secret_dir: Path) -> None:
    root = ET.fromstring(
        render_config(
            _seed("minimal", secret_dir),
            BASELINE,
            str(secret_dir),
            genesis_hashes=HASHES,
        )
    )
    # the fixture baseline declares none, so nothing is invented either
    assert root.find("system").findall("dnsserver") == []
