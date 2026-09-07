# Ansible Collection API Coverage

> Collection: `by_systems.opnsense` **v0.2.0**
> Wraps: [lib-opnsense](https://github.com/by-openclaw/lib-opnsense) v1.0.0
> Minimum OPNsense: **26.1**
> Last updated: 2026-04-11

## Summary

| Metric | Count |
|---|---|
| Total modules | 54 |
| Scopes | 12 |
| Roles | 11 |
| Modules DONE | 54 |
| Modules PLANNED | 0 |

---

## Status Legend

| Status | Meaning |
|---|---|
| `DONE` | Module implemented, tested, merged |
| `PLANNED` | Module not yet created |

---

## Auth (4 modules -- changes apply immediately)

| Scope | Module | Manager | Match Keys | Min OPNsense | Status |
|---|---|---|---|---|---|
| Auth | `opnsense_auth_user` | `AuthUserManager` | `name` | 26.1 | `DONE` |
| Auth | `opnsense_auth_group` | `AuthGroupManager` | `name` | 26.1 | `DONE` |
| Auth | `opnsense_auth_priv` | `AuthPrivManager` | `priv_id, target_type, target_name` | 26.1 | `DONE` |
| Auth | `opnsense_auth_api_key` | `AuthApiKeyManager` | `username` | 26.1 | `DONE` |

## Firewall (8 modules -- requires apply/reconfigure)

| Scope | Module | Manager | Match Keys | Min OPNsense | Status |
|---|---|---|---|---|---|
| Firewall | `opnsense_fw_alias` | `FwAliasManager` | `name` | 26.1 | `DONE` |
| Firewall | `opnsense_fw_filter` | `FwFilterManager` | `description, interface, direction, protocol` (+ optional `quick`, `sequence`, `source_not`, `destination_not`, `gateway` — omitted = untouched) | 26.1 | `DONE` |
| Firewall | `opnsense_fw_dnat` | `FwDnatManager` | `descr, interface, target` (+ source/destination net·port·not, sequence, natreflection, nordr, local_port) | 26.1 | `DONE` |
| Firewall | `opnsense_fw_source_nat` | `FwSourceNatManager` | `description, interface, source_net` | 26.1 | `DONE` |
| Firewall | `opnsense_fw_one_to_one` | `FwOneToOneManager` | `description, interface, source_net` | 26.1 | `DONE` |
| Firewall | `opnsense_fw_category` | `FwCategoryManager` | `name` | 26.1 | `DONE` |
| Firewall | `opnsense_fw_group` | `FwGroupManager` | `ifname` | 26.1 | `DONE` |
| Firewall | `opnsense_fw_npt` | `FwNptManager` | `source_net, destination_net` | 26.1 | `DONE` |

## Interfaces (9 modules -- requires reconfigure)

| Scope | Module | Manager | Match Keys | Min OPNsense | Status |
|---|---|---|---|---|---|
| Interfaces | `opnsense_if_vlan` | `IfVlanManager` | `tag, if` | 26.1 | `DONE` |
| Interfaces | `opnsense_if_vip` | `IfVipManager` | `address, interface, mode` | 26.1 | `DONE` |
| Interfaces | `opnsense_if_bridge` | `IfBridgeManager` | `descr` | 26.1 | `DONE` |
| Interfaces | `opnsense_if_gif` | `IfGifManager` | `tunnel-local-addr, tunnel-remote-addr` | 26.1 | `DONE` |
| Interfaces | `opnsense_if_gre` | `IfGreManager` | `tunnel-local-addr, tunnel-remote-addr` | 26.1 | `DONE` |
| Interfaces | `opnsense_if_lagg` | `IfLaggManager` | `descr` | 26.1 | `DONE` |
| Interfaces | `opnsense_if_loopback` | `IfLoopbackManager` | `description` | 26.1 | `DONE` |
| Interfaces | `opnsense_if_neighbor` | `IfNeighborManager` | `ipaddress, etheraddr` | 26.1 | `DONE` |
| Interfaces | `opnsense_if_vxlan` | `IfVxlanManager` | `vxlanid, vxlanlocal` | 26.1 | `DONE` |

## Routing (2 modules -- requires reconfigure)

| Scope | Module | Manager | Match Keys | Min OPNsense | Status |
|---|---|---|---|---|---|
| Routing | `opnsense_rt_gateway` | `RtGatewayManager` | `name` | 26.1 | `DONE` |
| Routing | `opnsense_rt_route` | `RtRouteManager` | `network, gateway` | 26.1 | `DONE` |

## DNS / Unbound (6 modules -- requires reconfigure)

| Scope | Module | Manager | Match Keys | Min OPNsense | Status |
|---|---|---|---|---|---|
| DNS | `opnsense_ub_host_override` | `UbHostOverrideManager` | `hostname, domain, server` | 26.1 | `DONE` |
| DNS | `opnsense_ub_host_alias` | `UbHostAliasManager` | `hostname, domain` | 26.1 | `DONE` |
| DNS | `opnsense_ub_forward` | `UbForwardManager` | `domain, server` | 26.1 | `DONE` |
| DNS | `opnsense_ub_acl` | `UbAclManager` | `name` | 26.1 | `DONE` |
| DNS | `opnsense_ub_dot` | `UbDotManager` | `server, port` | 26.1 | `DONE` |
| DNS | `opnsense_ub_diagnostics` | `UbDiagnosticsManager` | -- | 26.1 | `DONE` |

## DHCP / Kea (5 modules -- requires reconfigure)

| Scope | Module | Manager | Match Keys | Min OPNsense | Status |
|---|---|---|---|---|---|
| DHCP | `opnsense_kea4_subnet` | `Kea4SubnetManager` | `subnet` | 26.1 | `DONE` |
| DHCP | `opnsense_kea4_reservation` | `Kea4ReservationManager` | `ip_address, hw_address` | 26.1 | `DONE` |
| DHCP | `opnsense_kea4_peer` | `Kea4PeerManager` | `name` | 26.1 | `DONE` |
| DHCP | `opnsense_kea6_subnet` | `Kea6SubnetManager` | `subnet` | 26.1 | `DONE` |
| DHCP | `opnsense_kea6_reservation` | `Kea6ReservationManager` | `ip_address, duid` | 26.1 | `DONE` |

## WireGuard (2 modules -- requires reconfigure)

| Scope | Module | Manager | Match Keys | Min OPNsense | Status |
|---|---|---|---|---|---|
| WireGuard | `opnsense_wg_server` | `WgServerManager` | `name` | 26.1 | `DONE` |
| WireGuard | `opnsense_wg_client` | `WgClientManager` | `name` | 26.1 | `DONE` |

## IPsec (8 modules -- requires reconfigure)

| Scope | Module | Manager | Match Keys | Min OPNsense | Status |
|---|---|---|---|---|---|
| IPsec | `opnsense_ipsec_conn` | `IpsecConnManager` | `description` | 26.1 | `DONE` |
| IPsec | `opnsense_ipsec_child` | `IpsecChildManager` | `description` | 26.1 | `DONE` |
| IPsec | `opnsense_ipsec_local` | `IpsecLocalManager` | `description` | 26.1 | `DONE` |
| IPsec | `opnsense_ipsec_remote` | `IpsecRemoteManager` | `description` | 26.1 | `DONE` |
| IPsec | `opnsense_ipsec_psk` | `IpsecPskManager` | `description` | 26.1 | `DONE` |
| IPsec | `opnsense_ipsec_keypair` | `IpsecKeypairManager` | `name` | 26.1 | `DONE` |
| IPsec | `opnsense_ipsec_pool` | `IpsecPoolManager` | `name` | 26.1 | `DONE` |
| IPsec | `opnsense_ipsec_vti` | `IpsecVtiManager` | `description` | 26.1 | `DONE` |

## OpenVPN (1 module -- requires reconfigure)

| Scope | Module | Manager | Match Keys | Min OPNsense | Status |
|---|---|---|---|---|---|
| OpenVPN | `opnsense_ovpn_instance` | `OvpnInstanceManager` | `description` | 26.1 | `DONE` |

## Shaper (3 modules -- requires reconfigure)

| Scope | Module | Manager | Match Keys | Min OPNsense | Status |
|---|---|---|---|---|---|
| Shaper | `opnsense_ts_pipe` | `TsPipeManager` | `description, bandwidth, bandwidthMetric` | 26.1 | `DONE` |
| Shaper | `opnsense_ts_queue` | `TsQueueManager` | `description` | 26.1 | `DONE` |
| Shaper | `opnsense_ts_rule` | `TsRuleManager` | `description, interface, proto` | 26.1 | `DONE` |

## Trust / PKI (2 modules)

| Scope | Module | Manager | Match Keys | Min OPNsense | Status |
|---|---|---|---|---|---|
| Trust | `opnsense_trust_ca` | `TrustCaManager` | `descr` | 26.1 | `DONE` |
| Trust | `opnsense_trust_cert` | `TrustCertManager` | `descr` | 26.1 | `DONE` |

## Services (4 modules -- requires reconfigure)

| Scope | Module | Manager | Match Keys | Min OPNsense | Status |
|---|---|---|---|---|---|
| Services | `opnsense_cp_zone` | `CpZoneManager` | `description` | 26.1 | `DONE` |
| Services | `opnsense_cron_job` | `CronJobManager` | `description` | 26.1 | `DONE` |
| Services | `opnsense_ddns_account` | `DdnsAccountManager` | `description` | 26.1 | `DONE` |
| Services | `opnsense_syslog_dest` | `SyslogDestManager` | `description` | 26.1 | `DONE` |

> `opnsense_ddns_account` forwards the full lib model: `description, enabled,
> service, protocol, server, username, password, hostnames, checkip, interface,
> zone, resourceId, wildcard, checkip_timeout, force_ssl, ttl`. `zone` is required
> by the Cloudflare backend (provided by the `os-ddclient` plugin, which keeps the
> `/api/dyndns` MVC namespace).
