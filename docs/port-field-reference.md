# Port Field Reference

> Maps Ansible module parameters to OPNsense API field names for all modules
> that accept port values. Covers type expectations and validation behavior.
> Last updated: 2026-04-11

## Overview

Port handling in OPNsense varies by domain. Some modules accept only numeric
ports, others accept ranges (`80:443`), and firewall rules accept alias names
(e.g. a port alias defined in `opnsense_fw_alias`). This document clarifies
the mapping for every module with a port field.

---

## Field Mapping Table

| Module | Ansible Param | API Field | Ansible Type | Accepts | Notes |
|---|---|---|---|---|---|
| `opnsense_fw_filter` | `source_port` | `source_port` | str | numeric, range, alias | Alias must exist in fw_alias (type=port) |
| `opnsense_fw_filter` | `destination_port` | `destination_port` | str | numeric, range, alias | Alias must exist in fw_alias (type=port) |
| `opnsense_fw_source_nat` | `source_port` | `source_port` | str | numeric, range, alias | Same behavior as fw_filter |
| `opnsense_fw_source_nat` | `destination_port` | `destination_port` | str | numeric, range, alias | Same behavior as fw_filter |
| `opnsense_fw_dnat` | `destination_port` | `destination.port` | str | alias name, numeric, range | External (WAN) port to match |
| `opnsense_fw_dnat` | `source_port` | `source.port` | str | alias name, numeric, range | Source port to match |
| `opnsense_fw_dnat` | `local_port` | `local_port` | str | numeric, range | Internal target port; range uses colon separator |
| `opnsense_wg_server` | `listen_port` | `port` | int | numeric only | WireGuard tunnel listen port |
| `opnsense_wg_client` | `serverport` | `serverport` | int | numeric only | Remote WireGuard peer port |
| `opnsense_ovpn_instance` | `listen_port` | `port` | int | numeric only | OpenVPN listen port |
| `opnsense_syslog_dest` | `syslog_port` | `port` | str | numeric only | Default: `514` |
| `opnsense_ub_forward` | `forward_port` | `port` | str | numeric only | DNS forward target port |
| `opnsense_ub_dot` | `dot_port` | `port` | str | numeric only | Default: `853` (DNS-over-TLS) |
| `opnsense_ts_rule` | `src_port` | `src_port` | str | numeric, range, alias | Traffic shaper source port |
| `opnsense_ts_rule` | `dst_port` | `dst_port` | str | numeric, range, alias | Traffic shaper destination port |

---

## Type Categories

### Numeric only (int)

Modules that accept only a single integer port number. Passed to the API as a
string after `str()` conversion.

- `opnsense_wg_server.listen_port`
- `opnsense_wg_client.serverport`
- `opnsense_ovpn_instance.listen_port`

### Numeric only (str)

Modules that accept a port as a string but only expect numeric values. No
range or alias support.

- `opnsense_syslog_dest.syslog_port`
- `opnsense_ub_forward.forward_port`
- `opnsense_ub_dot.dot_port`

### Numeric, range, or alias (str)

Modules that accept a port number, a port range (colon-separated like
`8000:8080`), or the name of a port alias defined in `opnsense_fw_alias`.

- `opnsense_fw_filter.source_port`
- `opnsense_fw_filter.destination_port`
- `opnsense_fw_source_nat.source_port`
- `opnsense_fw_source_nat.destination_port`
- `opnsense_ts_rule.src_port`
- `opnsense_ts_rule.dst_port`

### Numeric or range (str)

Modules that accept a port number or a range but not an alias name.

- `opnsense_fw_dnat.local_port`

---

## Param Name vs API Field Name

Several modules rename the Ansible parameter to match the OPNsense API field.
This table shows only the cases where the names differ.

| Module | Ansible Param | API Field |
|---|---|---|
| `opnsense_wg_server` | `listen_port` | `port` |
| `opnsense_ovpn_instance` | `listen_port` | `port` |
| `opnsense_syslog_dest` | `syslog_port` | `port` |
| `opnsense_ub_forward` | `forward_port` | `port` |
| `opnsense_ub_dot` | `dot_port` | `port` |

Modules where the Ansible param name matches the API field name exactly:

- `opnsense_fw_filter`: `source_port`, `destination_port`
- `opnsense_fw_source_nat`: `source_port`, `destination_port`
- `opnsense_fw_dnat`: `local_port`
- `opnsense_wg_client`: `serverport`
- `opnsense_ts_rule`: `src_port`, `dst_port`
