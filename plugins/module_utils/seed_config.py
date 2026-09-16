# -*- coding: utf-8 -*-
# Copyright (c) BY-SYSTEMS SRL
# SPDX-License-Identifier: Apache-2.0
# Source: https://github.com/by-openclaw/ansible-opnsense
#
# OPNsense seed config.xml renderer.
#
# A fresh appliance cannot be configured over the API: on 26.7 `interfaces/assign/*`
# is 404, so interface assignment and per-interface addressing have no MVC controller.
# The config.xml therefore has to exist BEFORE the firewall is reachable — it is handed
# to the boot importer on a second disk (by_systems.opnsense.opnsense_seed_import).
#
# This module_utils renders that config.xml from a per-firewall seed profile. It is the
# logic that used to live in infra-terraform-proxmox modules/vm-opnsense/seed/build-seed.py,
# moved into the collection so a fresh firewall is built by `ansible-playbook` alone —
# no hand-run script (infra-terraform-proxmox #93).
#
# Behaviour is deliberately identical to the script it replaces: the slot layout
# (lan, trunk=opt1, VLANs opt2..optN, then the WANs, then FAB) is what the live
# firewalls and the ansible MVC catalog assign every rule and VLAN by. Changing it
# would land every rule on the wrong interface after a reseed.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import base64
import hashlib
import json
import os
import uuid
import xml.etree.ElementTree as ET


class SeedConfigError(Exception):
    """A seed profile, template or secret could not be turned into a config.xml."""


# Bootstrap creds (admin API key + password hashes) are injected at render time from
# the secret store, never committed. The baseline template holds placeholders.
BOOTSTRAP_SECRET_NAME = "OPNsense.seed-bootstrap.json"  # pragma: allowlist secret
_PLACEHOLDERS = {
    "__ROOT_PASSWORD_HASH__": "root_password_hash",  # pragma: allowlist secret
    "__BYRESEARCH_PASSWORD_HASH__": "byresearch_password_hash",  # pragma: allowlist secret
    "__BYRESEARCH_AUTHORIZEDKEYS__": "byresearch_authorizedkeys",  # pragma: allowlist secret
    "__SVCANSIBLE_AUTHORIZEDKEYS__": "svcansible_authorizedkeys",
}
# Secrets that live in OTHER fabric files: placeholder -> (file, field). The LDAP
# bind password is the Authentik LDAP outpost service account.
_EXTRA_PLACEHOLDERS = {
    "__LDAP_BIND_PASSWORD__": (
        "app-ldap-bind.json",
        "password",
    ),  # pragma: allowlist secret
}
# Genesis (break-glass oob-admin) credentials are COMPUTED at render time from a
# PER-SEED secret file: seed["genesis_creds_file"]. The seed only ever carries HASHES:
# the API secret as sha512-crypt (what OPNsense stores: "key|$6$..."), the GUI password
# as bcrypt. This is the ONE seeded API credential; svc-ansible's token is never seeded —
# it is minted from this one by ansible-platform roles/opnsense_api_bootstrap.
_GENESIS_PLACEHOLDERS = ("__OOBADMIN_APIKEYS__", "__OOBADMIN_PASSWORD_HASH__")

# Name of the static gateway rendered for a seed that declares one on the OOB port.
OOB_GATEWAY_NAME = "OOB_GW"


def resolve_secret(name, path, what, supplied=None):
    """Return a credential's fields, preferring what the caller supplied over a file.

    ``supplied`` is the Vault-sourced mapping the provisioning role passes in. Reading files
    is the break-glass fallback: Vault is the secret store, and a renderer that only ever read
    files is how an ISP password went stale in BOTH stores while only the running firewall held
    the working value (ansible-platform#360).
    """
    if supplied and name in supplied and supplied[name]:
        return supplied[name]
    return _read_json_fields(path, what)


def _read_json_fields(path, what):
    """Read a fabric secret file and return its ``fields`` mapping."""
    if not os.path.exists(path):
        raise SeedConfigError("%s not found: %s" % (what, path))
    try:
        data = json.loads(open(path, "r").read())
    except ValueError as exc:
        raise SeedConfigError("%s is not valid JSON: %s (%s)" % (what, path, exc))
    return data.get("fields", data)


def sha512_crypt_hash(secret):
    """Hash an API secret the way OPNsense stores it ($6$ sha512-crypt)."""
    try:
        import warnings

        warnings.simplefilter("ignore", DeprecationWarning)
        import crypt  # stdlib up to 3.12

        return crypt.crypt(secret, crypt.mksalt(crypt.METHOD_SHA512))
    except ImportError:  # 3.13+: crypt removed -> passlib
        try:
            from passlib.hash import sha512_crypt
        except ImportError:
            raise SeedConfigError(
                "no sha512-crypt implementation: python 3.13+ removed `crypt`, install passlib"
            )
        return sha512_crypt.using(rounds=5000).hash(secret)


def bcrypt_hash(password, rounds=10):
    """Hash a GUI password the way OPNsense stores it (bcrypt $2b$)."""
    try:
        import bcrypt
    except ImportError:
        raise SeedConfigError(
            "bcrypt is required to render the genesis GUI password hash"
        )
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds)).decode()


def _inject_genesis(text, seed, secret_dir, rounds=10, hashes=None, supplied=None):
    """Render the oob-admin genesis API key + GUI password hash into the config."""
    if not any(p in text for p in _GENESIS_PLACEHOLDERS):
        return text
    fname = seed.get("genesis_creds_file")
    if not fname:
        raise SeedConfigError(
            "baseline has genesis placeholders but the seed lacks 'genesis_creds_file'"
        )
    fpath = os.path.join(secret_dir, fname)
    fields = resolve_secret("genesis", fpath, "genesis secret file", supplied)
    for key in ("key", "secret", "webgui_password"):
        if not str(fields.get(key, "")).strip():
            raise SeedConfigError(
                "%s: missing/empty field '%s' (genesis)" % (fpath, key)
            )
    if hashes:  # tests pin the salts; production always hashes fresh
        api_hash, pw_hash = hashes["api"], hashes["webgui"]
    else:
        api_hash = sha512_crypt_hash(fields["secret"])
        pw_hash = bcrypt_hash(fields["webgui_password"], rounds)
    text = text.replace("__OOBADMIN_APIKEYS__", "%s|%s" % (fields["key"], api_hash))
    text = text.replace("__OOBADMIN_PASSWORD_HASH__", pw_hash)
    return text


def _inject_bootstrap_secrets(text, secret_dir, supplied=None):
    """Replace baseline placeholders with values from the secret store.

    Fail loud if a placeholder is present but its secret is missing — never ship a
    seed with an empty admin credential.
    """
    if not any(p in text for p in list(_PLACEHOLDERS) + list(_EXTRA_PLACEHOLDERS)):
        return text
    bootstrap = os.path.join(secret_dir, BOOTSTRAP_SECRET_NAME)
    fields = resolve_secret("bootstrap", bootstrap, "bootstrap secret", supplied)
    for ph, key in _PLACEHOLDERS.items():
        if ph in text:
            val = str(fields.get(key, "")).strip()
            if not val:
                raise SeedConfigError(
                    "%s: missing/empty field '%s' for %s" % (bootstrap, key, ph)
                )
            text = text.replace(ph, val)
    for ph, (fname, key) in _EXTRA_PLACEHOLDERS.items():
        if ph in text:
            fpath = os.path.join(secret_dir, fname)
            extra = resolve_secret(
                ph.strip("_").lower(), fpath, "secret file", supplied
            )
            val = str(extra.get(key, "")).strip()
            if not val:
                raise SeedConfigError(
                    "%s: missing/empty field '%s' for %s" % (fpath, key, ph)
                )
            text = text.replace(ph, val)
    return text


def _ip_network(prefix: int) -> int:
    # Used only for log/sanity; OPNsense doesn't need the network address.
    return prefix


def build_interfaces(seed: dict, supplied=None) -> ET.Element:
    """Emit <interfaces> matching OPNsense's serialization.

    Layout — matches the LIVE FW + the ansible MVC catalog (verified 2026-06-13):
      <lan>      = OOB management (vtnet1).                Always present.
      <opt1>     = SDN trunk (vtnet0) — VLAN parent.       Always present.
      <opt2..>   = VLANs hanging off the trunk (MGMT=opt2 … CCTV=opt11).
      <lo0>      = loopback.
      <opt12>    = WAN1 Proximus PPPoE (pppoe0).           Only if seed has "wan".
      <opt13>    = WAN2 Telenet static (vtnet3).           Only if seed has "wan2".
      <opt14>    = FAB fabric MGMT VLAN 600 (vtnet4).      Only if seed has "fab".

    The WANs are numbered AFTER the VLANs so the slot idents equal the running
    FW (Proximus=opt12, Telenet=opt13) and the ansible catalog — which assigns
    every rule/VLAN by these idents — applies correctly after a reseed. The old
    WAN-first numbering (Telenet=opt2, VLANs on opt3+) did NOT match live and
    would put every rule on the wrong interface on reseed.

    Track-Interface IPv6: when seed has "ipv6_pd_tracking", each internal NIC
    is configured to track WAN1's /56 PD with a unique sub-prefix ID.
    """
    pd = seed.get("ipv6_pd_tracking")
    ifs = ET.Element("interfaces")

    # lan = OOB management (with optional IPv6 tracking)
    lan = ET.SubElement(ifs, "lan")
    _lan(lan, seed["lan"], track6=_track6_for("lan", pd))

    # opt1 = LAN_TRUNK (VLAN parent, with optional IPv6 tracking)
    opt1 = ET.SubElement(ifs, "opt1")
    _trunk(opt1, seed["trunk"], track6=_track6_for("trunk", pd))

    # opt2..optN = VLANs FIRST (matches live/ansible: MGMT=opt2 … CCTV=opt11).
    # Minimal seed declares no VLANs — ansible/MVC adds them post-boot.
    opt_idx = 2
    for v in seed.get("vlans", []):
        opt = ET.SubElement(ifs, f"opt{opt_idx}")
        _opt(
            opt,
            v,
            ipv4_prefix=seed["ipv4_prefix"],
            ipv6_prefix=seed["ipv6_prefix"],
            track6=_track6_for(v["vlanif"], pd),
        )
        opt_idx += 1

    # lo0 — loopback (live serializes it between the VLANs and the WANs)
    lo = ET.SubElement(ifs, "lo0")
    ET.SubElement(lo, "internal_dynamic").text = "1"
    ET.SubElement(lo, "descr").text = "Loopback"
    ET.SubElement(lo, "enable").text = "1"
    ET.SubElement(lo, "if").text = "lo0"
    ET.SubElement(lo, "ipaddr").text = "127.0.0.1"
    ET.SubElement(lo, "ipaddrv6").text = "::1"
    ET.SubElement(lo, "subnet").text = "8"
    ET.SubElement(lo, "subnetv6").text = "128"
    ET.SubElement(lo, "type").text = "none"
    ET.SubElement(lo, "virtual").text = "1"

    # opt12 = WAN1 Proximus PPPoE — numbered after the VLANs to match the live FW.
    if "wan" in seed:
        wan = ET.SubElement(ifs, f"opt{opt_idx}")
        _wan(wan, seed["wan"])
        opt_idx += 1

    # opt13 = WAN2 Telenet static.
    if "wan2" in seed:
        wan2_node = ET.SubElement(ifs, f"opt{opt_idx}")
        _wan2(wan2_node, seed["wan2"], supplied)
        opt_idx += 1

    # opt14 = FAB fabric MGMT (vtnet4 -> vmbrFAB). Only if seed has "fab".
    if "fab" in seed:
        fab_node = ET.SubElement(ifs, f"opt{opt_idx}")
        _fab(fab_node, seed["fab"])
        opt_idx += 1

    return ifs


def _fab(node: ET.Element, f: dict) -> None:
    """OPNsense <opt14> = FAB — fabric MGMT (VLAN 600 = 10.6.240.0/20) on a dedicated
    physical NIC (vtnet4 -> vmbrFAB; the node bridges nic4.600, so untagged here).

    Static IPv4 only: no gateway, no IPv6, no DHCP. The fabric VRF (10.6.255.254)
    is the gateway; OPNsense is a member on the segment, not its router. Mirrors
    the LIVE prod block exactly (vm-opns-01, verified 2026-09-06): if, descr,
    enable, spoofmac, ipaddr, subnet — and nothing else. Prod = .2, test = .3.
    """
    ET.SubElement(node, "if").text = f["if"]
    ET.SubElement(node, "descr").text = f.get("descr", "FAB")
    ET.SubElement(node, "enable").text = "1"
    ET.SubElement(node, "spoofmac")
    ET.SubElement(node, "ipaddr").text = f["ipaddr"]
    ET.SubElement(node, "subnet").text = str(f.get("subnet", 20))


def _wan(node: ET.Element, w: dict) -> None:
    """OPNsense <wan> = ISP PPPoE interface. Proximus quirks baked in.

    Key Proximus-specific settings:
    - dhcp6-ia-pd-only = Proximus DHCPv6 only hands out PD, not IA_NA. Without
      this, dhcp6c logs 'advertise contains no address/prefix' and IPv6 fails.
    - dhcp6-prefix-id-statement matches Proximus's standard /56 delegation.
    - block_private/block_bogons MUST be ON: real internet exposure.
    """
    ET.SubElement(node, "if").text = w["if"]
    ET.SubElement(node, "descr").text = w.get("descr", "WAN")
    ET.SubElement(node, "enable").text = "1"
    ET.SubElement(node, "lock").text = "1"
    ET.SubElement(node, "ipaddr").text = w["ipv4"]
    ET.SubElement(node, "ipaddrv6").text = w["ipv6"]
    if w.get("block_private"):
        ET.SubElement(node, "blockpriv").text = "1"
    if w.get("block_bogons"):
        ET.SubElement(node, "blockbogons").text = "1"
    if w.get("mtu"):
        ET.SubElement(node, "mtu").text = str(w["mtu"])
    if w.get("mss"):
        ET.SubElement(node, "mss").text = str(w["mss"])
    if w["ipv6"] == "dhcp6":
        # Proximus DHCPv6 quirk: only IA_PD, no IA_NA
        if w.get("ipv6_dhcp6_ia_pd_only"):
            ET.SubElement(node, "dhcp6prefixonly").text = "1"
        prefix_hint = w.get("ipv6_prefix_hint", 56)
        ET.SubElement(node, "dhcp6-ia-pd-len").text = str(_pd_hint_to_len(prefix_hint))
        ET.SubElement(node, "dhcp6-ia-pd-send-hint").text = "1"
        if w.get("ipv6_send_rapid_commit"):
            ET.SubElement(node, "dhcp6-rapid-commit").text = "1"


def _wan_parent(node: ET.Element, p: dict) -> None:
    """OPNsense <opt> for the raw NIC under pppoe0.

    Assigned with no IP. block_private/block_bogons recommended so the raw
    layer also drops RFC1918/bogon traffic at the parent (defense in depth).
    """
    ET.SubElement(node, "if").text = p["if"]
    ET.SubElement(node, "descr").text = p.get("descr", "WAN1_Parent")
    ET.SubElement(node, "enable").text = "1"
    ET.SubElement(node, "lock").text = "1"
    if p.get("block_private"):
        ET.SubElement(node, "blockpriv").text = "1"
    if p.get("block_bogons"):
        ET.SubElement(node, "blockbogons").text = "1"


def _pd_hint_to_len(hint: int) -> int:
    """OPNsense expects the PD length in a 0-based scale (0 = /64, 8 = /56, ...).

    Empirically: dhcp6-ia-pd-len = 64 - hint. Most ISPs use /56 → len 8.
    """
    return max(0, 64 - int(hint))


def _lan(node: ET.Element, cfg: dict, *, track6: dict | None = None) -> None:
    """OPNsense <lan> = OOB admin network. DHCP from upstream, no block_private.

    If track6 is provided, IPv6 is set to "track6" mode and gets a /64 carved
    from the WAN1 /56 PD using the supplied prefix_id.
    """
    ET.SubElement(node, "if").text = cfg["if"]
    ET.SubElement(node, "descr").text = cfg.get("descr", "OOB_MGMT")
    ET.SubElement(node, "enable").text = "1"
    ET.SubElement(node, "ipaddr").text = cfg["ipv4"]
    if cfg.get("ipv4") not in ("dhcp", "none", ""):
        ET.SubElement(node, "subnet").text = str(cfg["ipv4_prefix"])
        # A statically addressed OOB port has no route unless the seed gives it one. On a
        # firewall whose only uplink IS the OOB port that route is what lets it reach the
        # firmware mirrors on first boot, so it belongs in the seed, not in a later apply.
        if cfg.get("ipv4_gateway"):
            ET.SubElement(node, "gateway").text = OOB_GATEWAY_NAME
    _emit_ipv6(node, cfg, track6=track6)


def _trunk(node: ET.Element, t: dict, *, track6: dict | None = None) -> None:
    """OPNsense <opt1> = LAN_TRUNK (vlan parent).

    A bare VLAN parent carries no IP — the VLAN interfaces hung off it (added by
    ansible) hold the addressing. When "ipv4" is omitted the trunk is emitted
    enabled with no address; ansible/MVC configures VLANs on top.
    """
    ET.SubElement(node, "if").text = t["if"]
    ET.SubElement(node, "descr").text = t.get("descr", "LAN_TRUNK")
    ET.SubElement(node, "enable").text = "1"
    if "ipv4" in t:
        ET.SubElement(node, "ipaddr").text = t["ipv4"]
        ET.SubElement(node, "subnet").text = str(t["ipv4_prefix"])
    if "ipv4" in t or "ipv6" in t or track6 is not None:
        _emit_ipv6(node, t, track6=track6)


def _opt(
    node: ET.Element,
    v: dict,
    *,
    ipv4_prefix: int,
    ipv6_prefix: int,
    track6: dict | None = None,
) -> None:
    ET.SubElement(node, "if").text = v["vlanif"]
    ET.SubElement(node, "descr").text = v["descr"]
    ET.SubElement(node, "enable").text = "1"
    ET.SubElement(node, "ipaddr").text = v["ipv4"]
    ET.SubElement(node, "subnet").text = str(v.get("ipv4_prefix", ipv4_prefix))
    _emit_ipv6(node, v, track6=track6, default_prefix=ipv6_prefix)


def _emit_ipv6(
    node: ET.Element,
    cfg: dict,
    *,
    track6: dict | None = None,
    default_prefix: int | None = None,
) -> None:
    """Emit IPv6 config — either static ULA, dhcp6, or track6 (PD sub-prefix).

    Precedence: track6 wins over the static ipv6 declared in the seed. This lets
    an internal NIC use both ULA-in-seed (for documentation) and Track-Interface-
    at-runtime (actual config), without duplicating the seed entry.
    """
    if track6 is not None:
        ET.SubElement(node, "ipaddrv6").text = "track6"
        ET.SubElement(node, "track6-interface").text = track6["track_source_slot"]
        ET.SubElement(node, "track6-prefix-id").text = track6["prefix_id"]
        return
    v6 = cfg.get("ipv6")
    if not v6:
        return
    ET.SubElement(node, "ipaddrv6").text = v6
    if v6 not in ("dhcp6", "none", "", "track6"):
        ET.SubElement(node, "subnetv6").text = str(
            cfg.get("ipv6_prefix", default_prefix or 64)
        )
    if v6 == "dhcp6":
        ET.SubElement(node, "dhcp6-ia-pd-len").text = "0"


def _track6_for(if_name: str, pd: dict | None) -> dict | None:
    """Look up Track-Interface config for an interface name in the seed's ipv6_pd_tracking."""
    if not pd:
        return None
    entry = pd.get("interfaces", {}).get(if_name)
    if entry is None:
        return None
    # Map track_source seed key ("wan") to OPNsense interface slot identifier
    return {
        "track_source_slot": pd.get("track_source", "wan"),
        "prefix_id": entry.get("prefix_id", "0x0"),
    }


def _wan2(node: ET.Element, w2: dict, supplied=None) -> None:
    """OPNsense static WAN2 (e.g. Telenet). Reads IPs from secret file at build time.

    No PPPoE — IPv4 and IPv6 are both static. Gateway is referenced by name
    (WAN2GW for IPv4, WAN2GWv6 for IPv6) — those gateway entries are emitted
    by build_gateways().
    """
    creds_path = w2.get("creds_secret")
    if not creds_path:
        raise SeedConfigError("wan2.creds_secret is required for static WAN2")
    creds = _read_wan_creds(creds_path, supplied)

    ET.SubElement(node, "if").text = w2["if"]
    ET.SubElement(node, "descr").text = w2.get("descr", "WAN2")
    ET.SubElement(node, "enable").text = "1"
    ET.SubElement(node, "lock").text = "1"
    if w2.get("block_private"):
        ET.SubElement(node, "blockpriv").text = "1"
    if w2.get("block_bogons"):
        ET.SubElement(node, "blockbogons").text = "1"
    # IPv4 static
    ET.SubElement(node, "ipaddr").text = creds["ipv4_address"]
    ET.SubElement(node, "subnet").text = str(creds["ipv4_prefix"])
    ET.SubElement(node, "gateway").text = "WAN_TELENET_GW"
    # IPv6 static (independent — not PPPoE-tracked)
    ET.SubElement(node, "ipaddrv6").text = creds["ipv6_address"]
    ET.SubElement(node, "subnetv6").text = str(creds["ipv6_prefix"])
    ET.SubElement(node, "gatewayv6").text = "WAN_TELENET_GWv6"


def compute_slot_map(seed: dict) -> dict:
    """Return a mapping from logical role → OPNsense slot identifier (lan|optN).

    Mirrors build_interfaces() so other generators (gateways, NAT, NetFlow) can
    reference the correct slot. Layout matches the LIVE FW + ansible catalog
    (verified 2026-06-13): trunk=opt1, VLANs=opt2..optN, then the WANs last —
    Proximus=opt12, Telenet=opt13. The ansible MVC catalog assigns rules/VLANs by
    these idents, so a reseed MUST reproduce them or every rule lands wrong.
    """
    slots = {}
    slots["lan"] = "lan"
    slots["trunk"] = "opt1"
    idx = 2
    # VLANs first → opt2..optN (MGMT=opt2 … CCTV=opt11).
    for v in seed.get("vlans", []):
        slots[v["vlanif"]] = f"opt{idx}"
        idx += 1
    # WANs last → Proximus=opt12, Telenet=opt13 (the live/ansible idents).
    if "wan" in seed:
        slots["wan"] = f"opt{idx}"
        idx += 1
    if "wan2" in seed:
        slots["wan2"] = f"opt{idx}"
        idx += 1
    # FAB last -> opt14 (fabric MGMT NIC; matches the live prod ident).
    if "fab" in seed:
        slots["fab"] = f"opt{idx}"
        idx += 1
    return slots


def _oob_gateway(seed: dict) -> ET.Element | None:
    """Static gateway for the OOB port, when the seed declares one.

    Default only when nothing else can be: a firewall with a WAN takes its default route
    from the ISP, and an OOB gateway that claimed it would blackhole every egress.
    """
    address = seed.get("lan", {}).get("ipv4_gateway")
    if not address:
        return None
    item = ET.Element("gateway_item")
    ET.SubElement(item, "interface").text = "lan"
    ET.SubElement(item, "gateway").text = address
    ET.SubElement(item, "name").text = OOB_GATEWAY_NAME
    ET.SubElement(item, "weight").text = "1"
    ET.SubElement(item, "ipprotocol").text = "inet"
    ET.SubElement(item, "descr").text = "OOB management gateway"
    ET.SubElement(item, "monitor_disable").text = "1"
    if "wan" not in seed and "wan2" not in seed:
        ET.SubElement(item, "defaultgw").text = "1"
    return item


def build_gateways(seed: dict, slot_map: dict, supplied=None) -> ET.Element | None:
    """Emit <gateways> block — primarily for static WAN2 (Telenet).

    WAN1 PPPoE auto-generates dynamic gateways (WAN1_PPPOE + WAN_DHCP6) on first
    boot when OPNsense processes the <wan> with ipaddr=pppoe — we don't need to
    declare them here. Only static gateways need explicit <gateway_item> entries.
    """
    oob = _oob_gateway(seed)
    w2 = seed.get("wan2")
    if not w2:
        if oob is None:
            return None
        gws = ET.Element("gateways")
        gws.append(oob)
        return gws
    creds = _read_wan_creds(w2["creds_secret"], supplied)
    wan2_slot = slot_map.get("wan2")
    if not wan2_slot:
        raise SeedConfigError(
            "wan2 has no slot in compute_slot_map — should not happen"
        )

    gws = ET.Element("gateways")

    # IPv4 gateway
    g4 = ET.SubElement(gws, "gateway_item")
    ET.SubElement(g4, "interface").text = wan2_slot
    ET.SubElement(g4, "gateway").text = creds["ipv4_gateway"]
    ET.SubElement(g4, "name").text = "WAN_TELENET_GW"
    ET.SubElement(g4, "weight").text = "1"
    ET.SubElement(g4, "ipprotocol").text = "inet"
    ET.SubElement(g4, "descr").text = w2.get("gateway_descr", "WAN2 gateway")
    ET.SubElement(g4, "monitor").text = creds["ipv4_gateway"]
    if w2.get("monitor_disable"):
        ET.SubElement(g4, "monitor_disable").text = "1"
    if w2.get("default_gateway_v4"):
        ET.SubElement(g4, "defaultgw").text = "1"

    # IPv6 gateway
    g6 = ET.SubElement(gws, "gateway_item")
    ET.SubElement(g6, "interface").text = wan2_slot
    ET.SubElement(g6, "gateway").text = creds["ipv6_gateway"]
    ET.SubElement(g6, "name").text = "WAN_TELENET_GWv6"
    ET.SubElement(g6, "weight").text = "1"
    ET.SubElement(g6, "ipprotocol").text = "inet6"
    ET.SubElement(g6, "descr").text = w2.get("gateway_descr", "WAN2 gateway")
    ET.SubElement(g6, "monitor").text = creds["ipv6_gateway"]
    if w2.get("monitor_disable"):
        ET.SubElement(g6, "monitor_disable").text = "1"
    if w2.get("default_gateway_v6"):
        ET.SubElement(g6, "defaultgw").text = "1"

    if oob is not None:
        gws.append(oob)

    return gws


def build_netflow(slot_map: dict) -> ET.Element:
    """Emit <OPNsense><Netflow> so a fresh seed boots with NetFlow/Insight active.

    The capture interface list is rendered from compute_slot_map (which now
    matches the live FW + ansible layout: VLANs opt2..opt11, Proximus opt12,
    Telenet opt13). Rendering from slot_map keeps capture = every internal + WAN
    ident and egress_only = the WAN idents correct no matter how many VLANs the
    seed defines, and guarantees the idents equal the running FW after a reseed.

    Why the seed and not Ansible MVC: the OPNsense diagnostics/netflow/setconfig
    endpoint is broken (returns {"result":"failed"} for every body shape) and root
    SSH is blocked, so the capture config cannot be asserted over the API. The seed
    writes config.xml directly, so it is the only reproducible home for it. On a
    fresh boot OPNsense reads this block; collect.enable=1 starts the local Insight
    aggregator (flowd_aggregate). Fields mirror the live getconfig model on
    vm-opns-01: NetFlow v9 -> 127.0.0.1:2056. Tracks ansible-platform #31.
    """

    def _order(ident: str) -> tuple:
        # Deterministic: OOB first, then optN by number, WAN/pppoe last.
        if ident == "lan":
            return (0, 0)
        if ident.startswith("opt"):
            return (1, int(ident[3:]))
        return (2, 0)

    wan_idents = [v for k, v in slot_map.items() if k in ("wan", "wan2", "wan_parent")]
    # FAB (fabric MGMT, opt14) is NOT captured — mirrors the live prod capture list
    # (lan,opt1..opt13); a management segment needs no flow accounting.
    capture = sorted([v for k, v in slot_map.items() if k != "fab"], key=_order)
    egress = sorted(wan_idents, key=_order)

    opnsense = ET.Element("OPNsense")
    nf = ET.SubElement(opnsense, "Netflow")
    cap = ET.SubElement(nf, "capture")
    ET.SubElement(cap, "interfaces").text = ",".join(capture)
    ET.SubElement(cap, "egress_only").text = ",".join(egress)
    ET.SubElement(cap, "version").text = "v9"
    ET.SubElement(cap, "targets").text = "127.0.0.1:2056"
    collect = ET.SubElement(nf, "collect")
    ET.SubElement(collect, "enable").text = "1"
    # OPNsense Netflow model defaults (live leaves them unset → these apply).
    ET.SubElement(nf, "activeTimeout").text = "1800"
    ET.SubElement(nf, "inactiveTimeout").text = "15"
    return opnsense


def _read_wan_creds(secret_path: str, supplied=None) -> dict:
    """Read static WAN credentials from a JSON secret file.

    Expected fields: ipv4_address, ipv4_prefix, ipv4_gateway, ipv6_address, ipv6_prefix, ipv6_gateway.
    Fails loudly if any required field is missing or empty.
    """
    f = resolve_secret("wan2", secret_path, "WAN secret file", supplied)
    required = (
        "ipv4_address",
        "ipv4_prefix",
        "ipv4_gateway",
        "ipv6_address",
        "ipv6_prefix",
        "ipv6_gateway",
    )
    missing = [k for k in required if not f.get(k)]
    if missing:
        raise SeedConfigError(f"{secret_path}: missing/empty fields: {missing}")
    return f


def _resolve_domain(seed: dict, supplied=None) -> str:
    """Resolve the DNS search domain at build time.

    Prefer `domain_secret` (path to a JSON secret with fields.domain) so the real
    internal domain never lands in the committed seed (no-real-domains rule). Fall
    back to the literal `domain` (placeholder) if no secret is configured.
    """
    secret_path = seed.get("domain_secret")
    if secret_path:
        f = resolve_secret("domain", secret_path, "domain secret file", supplied)
        domain = f.get("domain")
        if not domain:
            raise SeedConfigError(f"{secret_path}: missing/empty fields.domain")
        return domain
    return seed["domain"]


def build_vlans(seed: dict) -> ET.Element:
    """Emit <vlans> with one <vlan> child per seed entry. PCP per IEEE 802.1p."""
    parent_if = seed["physical_interfaces"]["trunk"]
    vlans = ET.Element("vlans")
    for v in seed.get("vlans", []):
        node = ET.SubElement(vlans, "vlan")
        ET.SubElement(node, "if").text = parent_if
        ET.SubElement(node, "tag").text = str(v["tag"])
        ET.SubElement(node, "pcp").text = str(v.get("pcp", 0))
        ET.SubElement(node, "proto").text = ""
        ET.SubElement(node, "descr").text = v["descr"]
        ET.SubElement(node, "vlanif").text = v["vlanif"]
    return vlans


def _read_pppoe_creds(secret_path: str, supplied=None) -> tuple[str, str]:
    """Read PPPoE username/password from a JSON secret file.

    Expected structure: {"fields": {"pppoe_username": "...", "pppoe_password": "..."}}.
    Raises with a clear message if the secret file or fields are missing — fail loud
    rather than ship a seed with empty credentials.
    """
    fields = resolve_secret("pppoe", secret_path, "PPPoE secret file", supplied)
    user = fields.get("pppoe_username", "").strip()
    pw = fields.get("pppoe_password", "").strip()
    if not user or not pw:
        raise SeedConfigError(
            f"pppoe_username or pppoe_password missing/empty in {secret_path}. "
            f"Fill them in (no label prefix, just the raw value)."
        )
    return user, pw


def build_ppps(seed: dict, supplied=None) -> ET.Element | None:
    """Emit <ppps> block with one <ppp> per PPPoE link.

    Returns None if seed has no "wan" with a pppoe_link_interface — i.e. we don't
    emit an empty <ppps> block on non-PPPoE seeds.
    """
    wan = seed.get("wan")
    if not wan or wan.get("ipv4") != "pppoe":
        return None

    link_if = wan.get("pppoe_link_interface")
    if not link_if:
        raise SeedConfigError("wan.pppoe_link_interface is required for PPPoE setup")

    secret_path = wan.get("pppoe_creds_secret")
    if not secret_path:
        raise SeedConfigError("wan.pppoe_creds_secret is required for PPPoE setup")
    user, pw = _read_pppoe_creds(secret_path, supplied)

    ppps = ET.Element("ppps")
    ppp = ET.SubElement(ppps, "ppp")
    ET.SubElement(ppp, "ptpid").text = "0"
    ET.SubElement(ppp, "type").text = "pppoe"
    ET.SubElement(ppp, "if").text = wan.get("if", "pppoe0")
    ET.SubElement(ppp, "ports").text = link_if
    ET.SubElement(ppp, "username").text = user
    ET.SubElement(ppp, "password").text = pw
    ET.SubElement(ppp, "provider").text = wan.get("pppoe_service_name", "")
    ET.SubElement(ppp, "mtu").text = str(wan.get("mtu", 1492))
    ET.SubElement(ppp, "mru").text = str(wan.get("mtu", 1492))
    return ppps


def build_interfaces_settings() -> ET.Element:
    """Emit <OPNsense><Interfaces><settings> — the 26.x global interface settings.

    Without this node a fresh seed boots with IPv6 BLOCKED: the legacy->MVC
    migration finds no <system><ipv6allow> and writes disableipv6=1, which
    activates the auto-rule "Block all IPv6" on every interface (test FW,
    2026-09-06: NDP to the Telenet router never resolved, fw log showed
    'block ... rule=Block all IPv6'). is_ipv6_allowed() in 26.7 reads exactly
    OPNsense/Interfaces/settings/disableipv6 (empty/0 = allowed).

    Values mirror the LIVE prod FW (vm-opns-01): hardware offloading disabled
    (virtio), VLAN hw filter disabled on parents (2), IPv6 allowed. The DHCPv6
    DUID is per-box and deliberately NOT seeded (OPNsense generates it).
    """
    ifs = ET.Element("Interfaces")
    st = ET.SubElement(
        ifs, "settings", version="1.0.0", description="Global interface settings"
    )
    for tag, val in (
        ("disablechecksumoffloading", "1"),
        ("disablesegmentationoffloading", "1"),
        ("disablelargereceiveoffloading", "1"),
        ("disablevlanhwfilter", "2"),
        ("disableipv6", "0"),
        ("dhcp6_norelease", "0"),
        ("dhcp6_debug", "0"),
        ("dhcp6_ratimeout", "10"),
    ):
        ET.SubElement(st, tag).text = val
    ET.SubElement(st, "dhcp6_duid")
    return ifs


def _self_signed_placeholder(fqdn, days=825):
    """A throw-away self-signed certificate for ``fqdn`` so the WebGUI has something valid to serve
    until the ACME client replaces it in place. RSA 2048 (lighttpd-safe everywhere)."""
    try:
        import datetime

        from cryptography import x509
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.x509.oid import NameOID
    except (
        ImportError
    ) as exc:  # pragma: no cover — the controller always ships cryptography
        raise SeedConfigError(
            "webgui_acme_fqdn needs the 'cryptography' package: %s" % exc
        )
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, fqdn)])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=days))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(fqdn)]), critical=False
        )
        .sign(key, hashes.SHA256())
    )
    crt_pem = cert.public_bytes(serialization.Encoding.PEM)
    key_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )
    return crt_pem, key_pem


def webgui_certificate_refid(fqdn):
    """Deterministic trust-store refid for the WebGUI certificate slot (13 hex chars, the
    uniqid() shape OPNsense uses). Stable across re-seeds so every consumer can find it."""
    return hashlib.sha1(fqdn.encode("utf-8")).hexdigest()[:13]  # nosec B324 — an id, not a secret


def build_webgui_certificate(root, seed):
    """Bind the WebGUI to the certificate the ACME client will issue — before it exists.

    System → Settings → Administration has no API, so the choice of GUI certificate is
    seed-owned. The trick: the ACME plugin reuses an existing trust-store refid when its
    certificate object already carries it (``LeCertificate::import``, verified on 26.7).
    So the seed pre-creates (1) a trust-store entry under a deterministic refid holding a
    self-signed placeholder for ``fqdn``, (2) ``system/webgui/ssl-certref`` pointing at it,
    and (3) a DISABLED ACME certificate object named ``fqdn`` with ``certRefId`` = that
    refid. The catalog then enables/completes the object and issues it; the leaf lands in
    the same slot and the GUI serves it. Re-runs: the catalog sees an issued, unchanged
    object and does nothing.
    """
    fqdn = str(seed.get("webgui_acme_fqdn", "") or "").strip()
    if not fqdn:
        return
    refid = webgui_certificate_refid(fqdn)
    crt_pem, key_pem = _self_signed_placeholder(fqdn)
    # (1) trust store entry
    for old in root.findall("cert"):
        if (old.findtext("refid") or "") == refid:
            root.remove(old)
    cert = ET.SubElement(root, "cert")
    ET.SubElement(cert, "refid").text = refid
    ET.SubElement(cert, "descr").text = "%s (ACME Client)" % fqdn
    ET.SubElement(cert, "crt").text = base64.b64encode(crt_pem).decode("ascii")
    ET.SubElement(cert, "csr").text = ""
    ET.SubElement(cert, "prv").text = base64.b64encode(key_pem).decode("ascii")
    # (2) the GUI serves that slot
    sys_node = root.find("system")
    webgui = sys_node.find("webgui")
    if webgui is None:
        webgui = ET.SubElement(sys_node, "webgui")
    certref = webgui.find("ssl-certref")
    if certref is None:
        certref = ET.SubElement(webgui, "ssl-certref")
    certref.text = refid
    # (3) the ACME certificate object, disabled until the catalog completes it
    opn = root.find("OPNsense")
    if opn is None:
        opn = ET.SubElement(root, "OPNsense")
    acme = opn.find("AcmeClient")
    if acme is None:
        acme = ET.SubElement(opn, "AcmeClient")
    certs = acme.find("certificates")
    if certs is None:
        certs = ET.SubElement(acme, "certificates")
    for old in list(certs):
        if (old.findtext("name") or "") == fqdn:
            certs.remove(old)
    obj = ET.SubElement(
        certs, "certificate", uuid=str(uuid.uuid5(uuid.NAMESPACE_DNS, fqdn))
    )
    fields = [
        ("id", uuid.uuid5(uuid.NAMESPACE_DNS, fqdn).hex[:14]),
        ("enabled", "0"),
        ("name", fqdn),
        (
            "description",
            "WebGUI certificate — slot seeded, issued by the catalog (opn_acme)",
        ),
        ("altNames", ""),
        ("account", ""),
        ("validationMethod", ""),
        ("keyLength", "key_4096"),
        ("ocsp", "0"),
        ("profile", ""),
        ("restartActions", ""),
        ("autoRenewal", "1"),
        ("renewInterval", "60"),
        ("aliasmode", "none"),
        ("domainalias", ""),
        ("challengealias", ""),
        ("certRefId", refid),
        ("lastUpdate", ""),
        ("statusCode", ""),
        ("statusLastUpdate", ""),
    ]
    for tag, val in fields:
        ET.SubElement(obj, tag).text = val


def render_config(
    seed, baseline_xml, secret_dir, bcrypt_rounds=10, genesis_hashes=None, secrets=None
):
    """Render a firewall's ``config.xml`` from its seed profile.

    :param seed: the parsed seed profile (per-firewall hardware + L2/L3 truth). ``dns_servers``,
        when present, replaces the baseline's resolvers — needed where the segment a firewall
        first boots on blocks external DNS.
    :param baseline_xml: the baseline template as text (placeholders still in it)
    :param secret_dir: directory holding the fabric secret files
    :param bcrypt_rounds: cost for the genesis GUI password hash
    :param genesis_hashes: pre-computed {"api", "webgui"} hashes — tests only, so a
        render is reproducible; production always hashes with a fresh salt
    :param secrets: credentials the caller already resolved, normally from Vault, keyed
        ``genesis`` / ``bootstrap`` / ``pppoe`` / ``wan2`` / ``domain`` / ``ldap_bind_password``.
        Anything supplied here wins; anything missing falls back to the file the seed names.
    :returns: the rendered XML as text, secrets injected
    """
    try:
        # the baseline is a template shipped in our own repository, never user input
        root = ET.fromstring(baseline_xml)  # nosec B314
    except ET.ParseError as exc:
        raise SeedConfigError("baseline template is not valid XML: %s" % exc)
    tree = ET.ElementTree(root)

    # Hostname / domain / timezone
    sys_node = root.find("system")
    if sys_node is not None:
        for tag, val in (
            ("hostname", seed["hostname"]),
            ("domain", _resolve_domain(seed, secrets)),
            ("timezone", seed["timezone"]),
        ):
            el = sys_node.find(tag)
            if el is None:
                el = ET.SubElement(sys_node, tag)
            el.text = val

    # Resolvers a fresh box uses before the catalog configures its own. The baseline carries a
    # public default, which is useless on a management segment that blocks external DNS — ours
    # does, so a firewall seeded there cannot reach the firmware mirrors at all. A seed that
    # names its own resolvers wins; one that says nothing keeps the baseline's.
    if seed.get("dns_servers") and sys_node is not None:
        for old_dns in sys_node.findall("dnsserver"):
            sys_node.remove(old_dns)
        for addr in seed["dns_servers"]:
            ET.SubElement(sys_node, "dnsserver").text = str(addr)

    # System → Settings → Administration knobs that have no API on 26.x, so the seed owns them:
    # the WebGUI's alternate hostnames (anything else trips the DNS-rebind check) and the sudo
    # policy for wheel (the CrowdSec bouncer key is the one file Ansible writes over SSH+become).
    # A seed that says nothing keeps the baseline's behaviour.
    if sys_node is not None:
        if seed.get("webgui_althostnames"):
            webgui = sys_node.find("webgui")
            if webgui is None:
                webgui = ET.SubElement(sys_node, "webgui")
            alt = webgui.find("althostnames")
            if alt is None:
                alt = ET.SubElement(webgui, "althostnames")
            alt.text = " ".join(str(h) for h in seed["webgui_althostnames"])
        if seed.get("sudo_allow_wheel") is not None:
            sudo = sys_node.find("sudo_allow_wheel")
            if sudo is None:
                sudo = ET.SubElement(sys_node, "sudo_allow_wheel")
            sudo.text = str(seed["sudo_allow_wheel"])
    # Replace interfaces + vlans + ppps + gateways (appended after <system>)
    for tag in ("interfaces", "vlans", "ppps", "gateways"):
        old = root.find(tag)
        if old is not None:
            root.remove(old)
    root.append(build_interfaces(seed, secrets))
    root.append(build_vlans(seed))
    ppps = build_ppps(seed, secrets)
    if ppps is not None:
        root.append(ppps)
    slot_map = compute_slot_map(seed)
    gws = build_gateways(seed, slot_map, secrets)
    if gws is not None:
        root.append(gws)

    # NetFlow/Insight capture block (plugin config lives under <OPNsense>).
    # Idempotent: drop any prior <Netflow>, (re)attach the slot-map-rendered one,
    # reusing an existing <OPNsense> parent if the baseline ever grows one.
    netflow_parent = build_netflow(slot_map)
    opnsense_node = root.find("OPNsense")
    if opnsense_node is None:
        root.append(netflow_parent)
    else:
        old_nf = opnsense_node.find("Netflow")
        if old_nf is not None:
            opnsense_node.remove(old_nf)
        opnsense_node.append(netflow_parent.find("Netflow"))

    # Global interface settings (IPv6 allowed, offloading off) under <OPNsense>.
    opnsense_node = root.find("OPNsense")
    old_ifs = opnsense_node.find("Interfaces")
    if old_ifs is not None:
        opnsense_node.remove(old_ifs)
    opnsense_node.append(build_interfaces_settings())

    # WebGUI certificate slot (seed-owned, see build_webgui_certificate)
    build_webgui_certificate(root, seed)
    ET.indent(tree, space="  ")
    text = ET.tostring(root, encoding="UTF-8", xml_declaration=True).decode("utf-8")
    return _inject_genesis(
        _inject_bootstrap_secrets(text, secret_dir, secrets),
        seed,
        secret_dir,
        rounds=bcrypt_rounds,
        hashes=genesis_hashes,
        supplied=secrets,
    )


def redact(text):
    """Blank every secret the renderer injects, so a diff can be shown safely."""
    out = []
    for line in text.splitlines():
        stripped = line.strip()
        for tag in ("password", "apikeys", "authorizedkeys", "secret"):
            if stripped.startswith("<%s>" % tag) and stripped.endswith("</%s>" % tag):
                line = line.split("<%s>" % tag)[0] + "<%s>REDACTED</%s>" % (tag, tag)
                break
        out.append(line)
    return "\n".join(out)
