# Modules

> All modules are thin wrappers around lib-opnsense managers.
> They translate Ansible parameters into `ensure()` calls and return structured results.
> 54 modules across 12 scopes. Requires OPNsense >= 26.1.

## Connection Parameters (shared)

All modules accept these connection parameters:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `host` | str | yes | -- | OPNsense hostname or IP |
| `key` | str | yes | -- | API key (`no_log: true`) |
| `secret` | str | yes | -- | API secret (`no_log: true`) |
| `port` | int | no | 443 | HTTPS port |
| `verify_ssl` | bool | no | false | Verify TLS certificate |

---

## Auth

### opnsense_auth_user

Manage local users: create, update, delete with idempotency.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | Username (unique) |
| `email` | str | no | "" | Email address |
| `description` | str | no | "" | User description |
| `password` | str | no | -- | Password (`no_log: true`) |
| `group_memberships` | str | no | "" | Comma-separated GIDs |
| `disabled` | bool | no | false | Disable account |
| `state` | str | no | present | `present` or `absent` |

### opnsense_auth_group

Manage local groups.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | Group name (unique) |
| `description` | str | no | "" | Group description |
| `state` | str | no | present | `present` or `absent` |

### opnsense_auth_priv

Assign or unassign privileges to users or groups.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `priv_id` | str | yes | -- | Privilege ID (e.g. `page-all`) |
| `target_type` | str | yes | -- | `user` or `group` |
| `target_name` | str | yes | -- | Name of the user or group |
| `state` | str | no | present | `present` (assign) or `absent` (unassign) |

### opnsense_auth_api_key

Create or delete API keys for users.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `username` | str | yes | -- | Username to manage keys for |
| `state` | str | no | present | `present` (create) or `absent` (delete all) |

**Returns** on create: `api_key` and `api_secret` (shown once, `no_log: true`).

---

## Firewall

### opnsense_fw_alias

Manage firewall aliases (hosts, networks, ports, URLs).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | Alias name (unique) |
| `type` | str | no | host | Alias type (host, network, port, url, etc.) |
| `content` | str | no | "" | Content -- IPs, networks, ports (newline-separated) |
| `description` | str | no | "" | Alias description |
| `enabled` | bool | no | true | Enable the alias |
| `proto` | str | no | "" | Protocol filter (IPv4, IPv6) |
| `state` | str | no | present | `present` or `absent` |

### opnsense_fw_filter

Manage firewall filter rules (pass/block/reject).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | -- | Rule description (used as match key) |
| `action` | str | no | pass | `pass`, `block`, or `reject` |
| `interface` | str | no | lan | Interface |
| `direction` | str | no | in | `in`, `out`, or `any` |
| `ipprotocol` | str | no | inet | `inet`, `inet6`, `inet46` |
| `protocol` | str | no | any | Transport protocol (TCP, UDP, etc.) |
| `source_net` | str | no | any | Source network or alias |
| `source_port` | str | no | "" | Source port (numeric, range, or alias) |
| `destination_net` | str | no | any | Destination network or alias |
| `destination_port` | str | no | "" | Destination port (numeric, range, or alias) |
| `enabled` | bool | no | true | Enable the rule |
| `log` | bool | no | false | Log matching packets |
| `state` | str | no | present | `present` or `absent` |

### opnsense_fw_dnat

Manage D-NAT / port forward rules.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `descr` | str | yes | -- | Rule description (match key -- note: `descr` not `description`) |
| `interface` | str | no | wan | Interface |
| `ipprotocol` | str | no | inet | IP version |
| `protocol` | str | no | tcp | Transport protocol |
| `target` | str | yes | -- | Internal target IP |
| `local_port` | str | no | "" | Internal target port (numeric or range) |
| `disabled` | bool | no | false | Disable the rule |
| `log` | bool | no | false | Log matching packets |
| `state` | str | no | present | `present` or `absent` |

Port-forward matching (added 0.3.0): `source_net`/`source_port`/`source_not`, `destination_net`/`destination_port`/`destination_not` (the WAN address + external port — alias names, `wanip`, interface-address keywords like `opt12ip`, or CIDR/number/range), `sequence`, `natreflection` (`purenat`/`disable`), `nordr`. Without `destination_*` the rule matches any destination — always set them for a real port forward.

### opnsense_fw_source_nat

Manage source NAT (outbound NAT / masquerade) rules.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | -- | Rule description (match key) |
| `interface` | str | no | wan | Interface |
| `ipprotocol` | str | no | inet | `inet` or `inet6` |
| `protocol` | str | no | any | Transport protocol |
| `source_net` | str | no | any | Source network |
| `source_port` | str | no | "" | Source port (numeric, range, or alias) |
| `destination_net` | str | no | any | Destination network |
| `destination_port` | str | no | "" | Destination port (numeric, range, or alias) |
| `target` | str | no | wanip | NAT target address |
| `enabled` | bool | no | true | Enable the rule |
| `log` | bool | no | false | Log matching packets |
| `state` | str | no | present | `present` or `absent` |

### opnsense_fw_one_to_one

Manage 1:1 NAT (binat) rules.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | -- | Rule description (match key) |
| `interface` | str | no | wan | Interface |
| `source_net` | str | yes | -- | Internal source network |
| `external` | str | no | "" | External IP address |
| `disabled` | bool | no | false | Disable the rule |
| `log` | bool | no | false | Log matching packets |
| `type` | str | no | binat | `binat` or `nat` |
| `destination_net` | str | no | "" | Destination network |
| `natreflection` | str | no | "" | `""`, `enable`, or `disable` |
| `state` | str | no | present | `present` or `absent` |

### opnsense_fw_category

Manage firewall rule categories.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | Category name (unique) |
| `color` | str | no | "" | Category color |
| `state` | str | no | present | `present` or `absent` |

### opnsense_fw_group

Manage firewall interface groups.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ifname` | str | yes | -- | Group interface name (unique) |
| `members` | str | yes | -- | Comma-separated member interfaces |
| `descr` | str | no | "" | Group description |
| `state` | str | no | present | `present` or `absent` |

### opnsense_fw_npt

Manage IPv6 NPTv6 (NAT66) prefix translation rules.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source_net` | str | yes | -- | Internal IPv6 prefix |
| `destination_net` | str | yes | -- | External IPv6 prefix |
| `interface` | str | yes | -- | Interface |
| `enabled` | bool | no | true | Enable the rule |
| `log` | bool | no | false | Log matching packets |
| `description` | str | no | "" | Rule description |
| `state` | str | no | present | `present` or `absent` |

---

## Interfaces

### opnsense_if_vlan

Manage 802.1Q VLAN sub-interfaces.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `tag` | int | yes | -- | VLAN tag (1-4094) |
| `if_parent` | str | yes | -- | Parent interface (maps to API field `if`) |
| `pcp` | int | no | 0 | Priority Code Point |
| `proto` | str | no | "" | `""`, `802.1q`, or `802.1ad` |
| `descr` | str | no | "" | VLAN description |
| `state` | str | no | present | `present` or `absent` |

### opnsense_if_vip

Manage virtual IP addresses (IP alias, CARP, proxy ARP).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `address` | str | yes | -- | IP address |
| `interface` | str | yes | -- | Interface |
| `mode` | str | yes | -- | `ipalias`, `carp`, or `proxyarp` |
| `network` | str | no | "" | Network mask / prefix |
| `descr` | str | no | "" | VIP description |
| `password` | str | no | "" | CARP password (`no_log: true`) |
| `advbase` | int | no | -- | CARP advertisement base |
| `advskew` | int | no | -- | CARP advertisement skew |
| `vhid` | str | no | "" | CARP VHID |
| `state` | str | no | present | `present` or `absent` |

### opnsense_if_bridge

Manage bridge interfaces.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `descr` | str | yes | -- | Bridge description (match key) |
| `state` | str | no | present | `present` or `absent` |

### opnsense_if_gif

Manage GIF tunnel interfaces.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `tunnel_local_addr` | str | yes | -- | Local tunnel address |
| `tunnel_remote_addr` | str | yes | -- | Remote tunnel address |
| `descr` | str | no | "" | Tunnel description |
| `state` | str | no | present | `present` or `absent` |

### opnsense_if_gre

Manage GRE tunnel interfaces.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `tunnel_local_addr` | str | yes | -- | Local tunnel address |
| `tunnel_remote_addr` | str | yes | -- | Remote tunnel address |
| `descr` | str | no | "" | Tunnel description |
| `state` | str | no | present | `present` or `absent` |

### opnsense_if_lagg

Manage link aggregation (LAGG) interfaces.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `descr` | str | yes | -- | LAGG description (match key) |
| `proto` | str | no | lacp | `none`, `lacp`, `failover`, `fec`, or `loadbalance` |
| `state` | str | no | present | `present` or `absent` |

### opnsense_if_loopback

Manage loopback interfaces.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | -- | Loopback description (match key) |
| `state` | str | no | present | `present` or `absent` |

### opnsense_if_neighbor

Manage static ARP / NDP neighbor entries.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ipaddress` | str | yes | -- | IP address |
| `etheraddr` | str | yes | -- | MAC address |
| `descr` | str | no | "" | Entry description |
| `state` | str | no | present | `present` or `absent` |

### opnsense_if_vxlan

Manage VXLAN tunnel interfaces.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `vxlanid` | int | yes | -- | VXLAN Network Identifier (VNI) |
| `vxlanlocal` | str | yes | -- | Local VTEP address |
| `vxlanremote` | str | no | "" | Remote VTEP address |
| `state` | str | no | present | `present` or `absent` |

---

## Routing

### opnsense_rt_gateway

Manage gateways.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | Gateway name (match key) |
| `interface` | str | no | "" | Interface |
| `gateway` | str | no | "" | Gateway IP address |
| `protocol` | str | no | inet | `inet` or `inet6` |
| `monitor_disable` | bool | no | false | Disable gateway monitoring |
| `descr` | str | no | "" | Gateway description |
| `disabled` | bool | no | false | Disable the gateway |
| `state` | str | no | present | `present` or `absent` |

### opnsense_rt_route

Manage static routes.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `network` | str | yes | -- | Destination network (match key) |
| `gateway` | str | yes | -- | Gateway name (match key) |
| `descr` | str | no | "" | Route description |
| `disabled` | bool | no | false | Disable the route |
| `state` | str | no | present | `present` or `absent` |

---

## DNS / Unbound

### opnsense_ub_host_override

Manage Unbound local DNS host overrides (A/AAAA/MX/TXT).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `hostname` | str | yes | -- | Hostname |
| `domain` | str | no | "" | Domain |
| `server` | str | no | "" | IP address (A/AAAA value) |
| `rr` | str | no | A | Record type: `A`, `AAAA`, `MX`, `TXT` |
| `mxprio` | str | no | "" | MX priority |
| `mx` | str | no | "" | MX target |
| `ttl` | str | no | "" | TTL override |
| `txtdata` | str | no | "" | TXT record data |
| `enabled` | bool | no | true | Enable the override |
| `description` | str | no | "" | Override description |
| `state` | str | no | present | `present` or `absent` |

### opnsense_ub_host_alias

Manage Unbound host aliases (CNAME-like).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `hostname` | str | yes | -- | Alias hostname |
| `domain` | str | no | "" | Alias domain |
| `host_uuid` | str | no | "" | Parent host override UUID (maps to API field `host`) |
| `enabled` | bool | no | true | Enable the alias |
| `description` | str | no | "" | Alias description |
| `state` | str | no | present | `present` or `absent` |

### opnsense_ub_forward

Manage Unbound domain-specific DNS forwarding.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `domain` | str | yes | -- | Domain to forward |
| `server` | str | no | "" | Upstream server IP |
| `type` | str | no | forward | `forward` or `stub` |
| `forward_port` | str | no | "" | Upstream server port (maps to API field `port`) |
| `enabled` | bool | no | true | Enable the forwarder |
| `description` | str | no | "" | Forwarder description |
| `state` | str | no | present | `present` or `absent` |

### opnsense_ub_acl

Manage Unbound DNS access control lists.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | ACL name (unique) |
| `action` | str | no | allow | `allow`, `deny`, `refuse`, `allow_snoop`, `deny_non_local`, `refuse_non_local` |
| `networks` | str | no | "" | Comma-separated network list |
| `enabled` | bool | no | true | Enable the ACL |
| `description` | str | no | "" | ACL description |
| `state` | str | no | present | `present` or `absent` |

### opnsense_ub_dot

Manage Unbound DNS-over-TLS upstream servers.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `server` | str | yes | -- | Upstream server IP |
| `dot_port` | str | no | 853 | DoT port (maps to API field `port`) |
| `type` | str | no | dot | Server type (only `dot`) |
| `verify` | str | no | "" | Verify hostname |
| `domain` | str | no | "" | Server domain |
| `enabled` | bool | no | true | Enable the server |
| `description` | str | no | "" | Server description |
| `state` | str | no | present | `present` or `absent` |

### opnsense_ub_settings

Manage the Unbound resolver's `general` settings (singleton — only the options you set are diffed and sent). A freshly installed or seeded firewall ships with the resolver **disabled**; this module turns it on.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `enabled` | bool | no | -- | Enable the resolver |
| `listen_port` | str | no | -- | Listening port (maps to API field `port`; `port` is the API connection port) |
| `active_interface` | list[str] | no | -- | Interface slot ids to listen on (empty list = all) |
| `outgoing_interface` | list[str] | no | -- | Interface slot ids for upstream queries (empty list = all) |
| `stats` | bool | no | -- | Collect statistics |
| `dnssec` | bool | no | -- | DNSSEC validation |
| `dns64` | bool | no | -- | DNS64 synthesis |
| `dns64prefix` | str | no | -- | DNS64 prefix |
| `noarecords` | bool | no | -- | Do not return A records |
| `regdhcp` | bool | no | -- | Register DHCP leases |
| `regdhcpdomain` | str | no | -- | Domain for registered DHCP names |
| `regdhcpstatic` | bool | no | -- | Register static DHCP mappings |
| `noreglladdr6` | bool | no | -- | Skip IPv6 link-local registration |
| `noregrecords` | bool | no | -- | Skip system A/AAAA registration |
| `txtsupport` | bool | no | -- | TXT records for DHCP descriptions |
| `cacheflush` | bool | no | -- | Flush cache on reload |
| `safesearch` | bool | no | -- | Force SafeSearch |
| `enable_wpad` | bool | no | -- | Serve WPAD records |
| `local_zone_type` | str | no | -- | `always_nxdomain`, `always_refuse`, `always_transparent`, `deny`, `inform`, `inform_deny`, `nodefault`, `refuse`, `static`, `transparent`, `typetransparent` |
| `state` | str | no | present | Only `present` (singleton) |

### opnsense_ub_service

Control the Unbound service. Reports `disabled` while the resolver is off in its settings — enable it with `opnsense_ub_settings` first. `reconfigured` always applies (never idempotent by design).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `state` | str | no | running | `running`, `stopped` or `reconfigured` |

### opnsense_chrony_settings

Chrony NTP (os-chrony) general settings (singleton — only the options you set are diffed and sent). Requires `os-chrony`.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `enabled` | bool | no | -- | Enable chronyd. |
| `ntp_port` | str | no | -- | NTP port (API field C(port); 123 to serve clients). (API field `port`) |
| `nts_client` | bool | no | -- | Use NTS for upstream peers. (API field `ntsclient`) |
| `nts_nocert` | bool | no | -- | Skip NTS certificate validation. (API field `ntsnocert`) |
| `peers` | list[str] | no | -- | Upstream NTP peers (pool hostnames). |
| `fallback_peers` | str | no | -- | Fallback peers (CSV). (API field `fallbackpeers`) |
| `allowed_networks` | list[str] | no | -- | Networks chronyd serves NTP to (empty = client-only). (API field `allowednetworks`) |
| `state` | str | no | present | Only `present` (singleton) |

### opnsense_chrony_service

Control the Chrony NTP service (`os-chrony`). Reports `disabled` while switched off in its settings; `reconfigured` always applies.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `state` | str | no | running | `running`, `stopped` or `reconfigured` |

### opnsense_lldpd_settings

LLDP daemon (os-lldpd) general settings (singleton — only the options you set are diffed and sent). Requires `os-lldpd`.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `enabled` | bool | no | -- | Enable lldpd. |
| `cdp` | bool | no | -- | Also speak CDP (Cisco). |
| `fdp` | bool | no | -- | Also speak FDP (Foundry). |
| `edp` | bool | no | -- | Also speak EDP (Extreme). |
| `sonmp` | bool | no | -- | Also speak SONMP (Nortel). |
| `agentx` | bool | no | -- | Expose an SNMP AgentX sub-agent. |
| `interfaces` | list[str] | no | -- | Interface slot ids to announce on (API field C(interface), CSV). (API field `interface`) |
| `state` | str | no | present | Only `present` (singleton) |

### opnsense_lldpd_service

Control the LLDP daemon service (`os-lldpd`). Reports `disabled` while switched off in its settings; `reconfigured` always applies.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `state` | str | no | running | `running`, `stopped` or `reconfigured` |

### opnsense_qemuguestagent_settings

QEMU guest agent (os-qemu-guest-agent) settings (singleton — only the options you set are diffed and sent). Requires `os-qemu-guest-agent`.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `enabled` | bool | no | -- | Enable the guest agent. (API field `Enabled`) |
| `log_debug` | bool | no | -- | Debug logging. (API field `LogDebug`) |
| `disabled_rpcs` | list[str] | no | -- | guest-* RPC names to block (e.g. guest-exec). (API field `DisabledRPCs`) |
| `state` | str | no | present | Only `present` (singleton) |

### opnsense_qemuguestagent_service

Control the QEMU guest agent service (`os-qemu-guest-agent`). Reports `disabled` while switched off in its settings; `reconfigured` always applies.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `state` | str | no | running | `running`, `stopped` or `reconfigured` |

### opnsense_dnscrypt_settings

dnscrypt-proxy (os-dnscrypt-proxy) general settings (singleton — only the options you set are diffed and sent). Requires `os-dnscrypt-proxy`.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `enabled` | bool | no | -- | Enable dnscrypt-proxy. |
| `listen_addresses` | list[str] | no | -- | Listen addresses (e.g. 127.0.0.1:53531, [::1]:53531). |
| `serverlist` | list[str] | no | -- | Upstream server names from the public-resolvers list (free-form CSV on the API — not validated against the downloaded list). |
| `disabled_serverlist` | list[str] | no | -- | Server names to exclude. |
| `relaylist` | list[str] | no | -- | Anonymized DNS relays. |
| `ipv4_servers` | bool | no | -- | Use IPv4 upstream servers. |
| `ipv6_servers` | bool | no | -- | Use IPv6 upstream servers. |
| `dnscrypt_servers` | bool | no | -- | Use DNSCrypt servers. |
| `doh_servers` | bool | no | -- | Use DoH servers. |
| `odoh_servers` | bool | no | -- | Use ODoH servers. |
| `require_dnssec` | bool | no | -- | Only DNSSEC-validating servers. |
| `require_nolog` | bool | no | -- | Only no-log servers. |
| `require_nofilter` | bool | no | -- | Only non-filtering servers. |
| `force_tcp` | bool | no | -- | Force TCP upstream. |
| `cache` | bool | no | -- | Enable the local cache. |
| `cache_size` | str | no | -- | Cache size (entries). |
| `cache_min_ttl` | str | no | -- | Cache min TTL. |
| `cache_max_ttl` | str | no | -- | Cache max TTL. |
| `cache_neg_min_ttl` | str | no | -- | Negative cache min TTL. |
| `cache_neg_max_ttl` | str | no | -- | Negative cache max TTL. |
| `fallback_resolver` | str | no | -- | Bootstrap resolver (ip:port). |
| `timeout` | str | no | -- | Query timeout (ms). |
| `keepalive` | str | no | -- | Keepalive (s). |
| `cert_refresh_delay` | str | no | -- | Certificate refresh delay (min). |
| `query_logs` | bool | no | -- | Log every query (audit). |
| `block_ipv6` | bool | no | -- | Block AAAA answers. |
| `allow_privileged` | bool | no | -- | Allow binding privileged ports. (API field `allowprivileged`) |
| `max_clients` | str | no | -- | Max concurrent clients. |
| `dnscrypt_ephemeral_keys` | bool | no | -- | Ephemeral DNSCrypt keys. |
| `tls_disable_session_tickets` | bool | no | -- | Disable TLS session tickets. |
| `proxy` | str | no | -- | SOCKS proxy URL. |
| `state` | str | no | present | Only `present` (singleton) |

### opnsense_dnscrypt_service

Control the dnscrypt-proxy service (`os-dnscrypt-proxy`). Reports `disabled` while switched off in its settings; `reconfigured` always applies.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `state` | str | no | running | `running`, `stopped` or `reconfigured` |

### opnsense_plugin

Install or remove an `os-*` plugin through the firmware job API and wait for it. The backend reports `done` even for a REFUSED job (fresh 26.7.0 image: "Installation out of date…", unknown package) — the verdict is read from the job log and surfaced as a failure.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | Plugin package name |
| `wait` | bool | no | true | Wait for the job and verify |
| `timeout` | int | no | 300 | Job timeout (s) |
| `state` | str | no | present | `present` or `absent` |

### opnsense_firmware

Run the firmware check and apply the pending point update (`updated`) or major upgrade (`upgraded`) only when the device reports one; the device reboots. With `target` set, waits until `product_version` contains it. In check mode nothing is fired and `diff.before` carries the resolved status. A deliberate per-environment window, never part of a routine converge.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `target` | str | no | -- | Version substring to wait for after the reboot |
| `check_timeout` | int | no | 120 | Check job timeout (s) |
| `wait_timeout` | int | no | 1500 | Reboot wait timeout (s) |
| `state` | str | no | updated | `updated` or `upgraded` |

### opnsense_core_service

Start / stop / restart a daemon registered in `core/service/search` (legacy daemons without an MVC controller, e.g. `ntpd`). Unknown daemon = stopped.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | Service id |
| `state` | str | no | running | `running`, `stopped` or `restarted` |

### opnsense_ddns_service

Control the Dynamic DNS (os-ddclient) service; `restarted` publishes the active WAN address immediately.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `state` | str | no | reconfigured | `running`, `stopped`, `restarted` or `reconfigured` |

### opnsense_netflow_service

Reconfigure the NetFlow / Insight exporter (the exporter configuration itself is seed-owned).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `state` | str | no | reconfigured | `reconfigured` (only meaningful state) |

### opnsense_monit_settings

Manage the Monit `general` block (singleton — only the options you set are sent).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `enabled` | bool | no | -- | Enable Monit |
| `interval / startdelay` | str | no | -- | Poll interval / start delay (s) |
| `mailserver / smtp_port / username / password / ssl / sslversion / sslverify` | str/bool | no | -- | SMTP alert transport (`smtp_port` → API `port`; `password` no_log) |
| `httpd_enabled / httpd_port / httpd_username / httpd_password / httpd_allow` | bool/str | no | -- | Monit HTTP interface |
| `mmonit_url / mmonit_timeout / mmonit_register_credentials` | str/bool | no | -- | M/Monit |
| `logfile / statefile / eventqueue_path / eventqueue_slots` | str | no | -- | Files / event queue |
| `state` | str | no | present | Only `present` |

### opnsense_monit_alert

CRUD Monit alert recipients (matched by `recipient`).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `recipient` | str | yes | -- | Recipient e-mail (match key) |
| `enabled` | bool | no | -- | Enable |
| `noton` | bool | no | -- | Invert the event selection |
| `events` | str | no | -- | Comma-separated events (empty = all) |
| `format` | str | no | -- | Custom mail format |
| `reminder` | str | no | -- | Reminder cycles |
| `description` | str | no | -- | Description |
| `state` | str | no | present | `present` or `absent` |

### opnsense_monit_test

CRUD Monit tests (matched by `name`). OPNsense coerces `type` to `Custom` when `condition` is not one of the type's fixed expressions (`Existence` expects `not exist`) — use `Custom` for free-form conditions such as `does not exist`, or the second run reports a change.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | Test name (match key) |
| `type` | str | no | -- | Existence, SystemResource, ProcessResource, … (see module doc) |
| `condition` | str | no | -- | Condition expression |
| `action` | str | no | -- | alert, restart, start, stop, exec, unmonitor |
| `path` | str | no | -- | Path for exec |
| `state` | str | no | present | `present` or `absent` |

### opnsense_monit_service

CRUD Monit monitored services / checks (matched by `name`). `tests` / `depends` are comma-separated UUIDs.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | Service name (match key) |
| `type` | str | no | -- | process, file, fifo, filesystem, directory, host, system, custom, network |
| `enabled / description` | bool/str | no | -- |  |
| `pidfile / match / path / address / interface` | str | no | -- | Type-specific target |
| `timeout / starttimeout / polltime` | str | no | -- | Timings |
| `tests / depends` | str | no | -- | Comma-separated UUIDs |
| `start / stop` | str | no | -- | Commands |
| `state` | str | no | present | `present` or `absent` |

### opnsense_monit_daemon

Control the Monit daemon (`os-monit`) — the process, not the monitored-service entries. `reconfigured` regenerates `monitrc`, runs the syntax test and (re)starts; a refused config (plugin answers HTTP 200 `status: failed`) fails the task with the plugin's message. `reconfigured` always applies.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `state` | str | no | running | `running`, `stopped` or `reconfigured` |

### opnsense_seed_import

Seed a **fresh** OPNsense VM on Proxmox VE. A freshly imaged appliance has no API, no SSH and no
configuration, so the only way to hand it a `config.xml` is its own boot-time importer — which gates
on a keypress (upstream `src/sbin/opnsense-importer`). This module boots the VM, waits for the
importer prompt, sends one carriage return, answers the device prompt, and returns once the appliance
reports it is restoring. Everything after that first boot is ordinary API work.

One-shot by nature: a successful run always reports `changed`. Needs `websocket-client` on the
controller. Ordering is enforced — nothing is sent before its prompt, because early input pollutes the
appliance's buffer and the import fails.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `pve_host` | str | yes | -- | Proxmox API host |
| `pve_port` | int | no | 8006 | Proxmox API port |
| `pve_node` | str | yes | -- | Node the VM lives on |
| `pve_token_id` / `pve_token_secret` | str | yes | -- | API token (secret is `no_log`) |
| `validate_certs` | bool | no | false | Verify the Proxmox API certificate |
| `vmid` | int | yes | -- | VM to seed |
| `device` | str | no | vtbd1 | Device holding the configuration, as the appliance sees it |
| `start_vm` | bool | no | true | Start the VM if it is not running |
| `timeout` | int | no | 600 | Seconds to wait for the restore to begin |
| `settle` | int | no | 45 | Seconds to let the import and boot finish |

### opnsense_acme_settings

ACME client (`os-acme-client`) general settings (singleton — only the options you set are diffed and sent). The lib reconfigures the service after a change, which regenerates the acme.sh configuration and the renewal cron.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `enabled` | bool | no | -- | Master enable |
| `auto_renewal` | bool | no | -- | Auto-renewal cron |
| `environment` | str | no | -- | `""` (default), `prod`, `stg` |
| `challenge_port` / `tls_challenge_port` | str | no | -- | Internal challenge ports |
| `restart_timeout` | str | no | -- | Seconds to wait for restarts |
| `haproxy_integration` | bool | no | -- | HAProxy integration |
| `log_level` | str | no | -- | `normal`, `extended`, `debug`, `debug2`, `debug3` |
| `show_intro` | bool | no | -- | GUI intro panel |
| `cron` | bool | no | false | Converge the auto-renewal cron job via the plugin's `fetchCronIntegration` (the only way it is created) |

### opnsense_acme_account

ACME CA accounts (match key `name`). `state: registered` = present + register with the CA when the last status is not `200` (idempotent).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | Match key |
| `email` | str | no | -- | Contact e-mail |
| `ca` | str | no | -- | `letsencrypt`, `letsencrypt_test`, `buypass`, `buypass_test`, `google`, `google_test`, `sslcom`, `zerossl`, `custom` |
| `custom_ca` | str | no | -- | Directory URL for `custom` |
| `eab_kid` / `eab_hmac` | str | no | -- | External Account Binding (no_log) |
| `enabled` | bool | no | -- | Enable |
| `state` | str | no | present | `present`, `absent`, `registered` |

### opnsense_acme_validation

ACME challenge methods (match key `name`). Cloudflare DNS-01: `method: dns01`, `dns_service: dns_cf`, `dns_cf_token` (scoped token), `dns_cf_account_id`, optional `dns_cf_zone_id`, `dns_sleep`.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | Match key |
| `method` | str | no | -- | `http01`, `dns01`, `tlsalpn01` |
| `http_service`, `http_opn_autodiscovery`, `http_opn_interface`, `http_opn_ipaddresses` | | no | -- | HTTP-01 options |
| `dns_service`, `dns_sleep`, `dns_cf_email`, `dns_cf_key`, `dns_cf_token`, `dns_cf_account_id`, `dns_cf_zone_id` | str | no | -- | DNS-01 options (secrets no_log) |
| `enabled` | bool | no | -- | Enable |
| `state` | str | no | present | `present`, `absent` |

### opnsense_acme_action

ACME post-issue automations (match key `name`). `type: configd_restart_gui` restarts the WebGUI after a certificate update; SFTP / remote-SSH upload types pass their target fields through.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | Match key |
| `type` | str | no | -- | `configd_restart_gui`, `configd_restart_haproxy`, `configd_generic`, `configd_upload_sftp`, `configd_remote_ssh`, … |
| `enabled` | bool | no | -- | Enable |
| `sftp_*` / `remote_ssh_*` / `configd_generic_command` | str | no | -- | Target fields per type |
| `state` | str | no | present | `present`, `absent` |

### opnsense_acme_certificate

ACME certificates (match key `name` = primary domain). `account`, `validation_method`, `restart_actions` take UUIDs (read-only lookup first). `state: issued` = present + sign when no issued leaf exists yet (`certRefId` empty or last status not `200`) — an issued, unchanged certificate is a noop; `renew: true` signs again (explicit renewal, never idempotent). Signing talks to the CA and can take minutes (DNS-01 `dns_sleep`).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | Primary domain (match key) |
| `alt_names` | str | no | -- | SANs, comma-separated |
| `account` / `validation_method` / `restart_actions` | str | no | -- | UUID references |
| `key_length` | str | no | -- | `key_2048`, `key_3072`, `key_4096`, `key_ec256`, `key_ec384` |
| `ocsp` | bool | no | -- | OCSP Must-Staple |
| `auto_renewal` / `renew_interval` | bool / str | no | -- | Renewal policy |
| `aliasmode`, `domainalias`, `challengealias` | str | no | -- | Alias mode |
| `enabled` | bool | no | -- | Enable |
| `renew` | bool | no | false | With `issued`: sign again |
| `state` | str | no | present | `present`, `absent`, `issued` |

### opnsense_acme_service

Control the ACME client service. `reconfigured` regenerates the acme.sh configuration and the renewal cron; it always applies.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `state` | str | no | running | `running`, `stopped` or `reconfigured` |

### opnsense_kea4_settings

Manage the Kea DHCPv4 `general` block (singleton — only the options you set are sent). A freshly seeded FW ships Kea disabled.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `enabled` | bool | no | -- | Enable the DHCPv4 daemon |
| `interfaces` | list[str] | no | -- | Interface slot ids to listen on |
| `valid_lifetime` | str | no | -- | Lease lifetime (s) |
| `fwrules` | bool | no | -- | Plugin-managed pass rules |
| `manual_config` | bool | no | -- | Hand-written kea config |
| `dhcp_socket_type` | str | no | -- | `raw` or `udp` |
| `compatibility` | list[str] | no | -- | Compatibility flags |
| `decline_probation_period / service_sockets_*` | str | no | -- | Advanced timers |
| `state` | str | no | present | Only `present` |

### opnsense_kea6_settings

Manage the Kea DHCPv6 `general` block. Kea v6 emits no router advertisements — pair with `opnsense_radvd_entry`.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `enabled` | bool | no | -- | Enable the DHCPv6 daemon |
| `interfaces` | list[str] | no | -- | Interface slot ids |
| `valid_lifetime` | str | no | -- | Lease lifetime (s) |
| `fwrules / manual_config` | bool | no | -- |  |
| `mac_sources` | list[str] | no | -- | MAC sources (default `ipv6-link-local`) |
| `state` | str | no | present | Only `present` |

### opnsense_kea_service

Control the Kea DHCP service (v4 + v6 share one controller); `disabled` while both families are off.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `state` | str | no | running | `running`, `stopped` or `reconfigured` |

### opnsense_radvd_entry

CRUD radvd entries (matched by `interface`).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `interface` | str | yes | -- | Interface slot id (match key) |
| `enabled` | bool | no | -- | Enable |
| `mode` | str | no | -- | router, unmanaged, managed, assist, stateless |
| `base6_interface` | str | no | -- | Track this interface's prefix (API `Base6Interface`) |
| `deprecate_prefix / remove_adv_on_exit / remove_route` | str | no | -- | `on`/`off`/empty |
| `state` | str | no | present | `present` or `absent` |

### opnsense_radvd_service

Control radvd.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `state` | str | no | running | `running`, `stopped` or `reconfigured` |

### opnsense_dnsmasq_settings

Manage the Dnsmasq global settings singleton. Keep it off or strictly bound while Kea holds 67/547 and Unbound owns :53.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `enable` | bool | no | -- | Master switch |
| `strictbind` | bool | no | -- | Bind only listed interfaces |
| `interface` | list[str] | no | -- | Interface slot ids |
| `listen_port` | str | no | -- | Port (API `port`) |
| `dns_port` | str | no | -- | DNS port |
| `dhcp` | list[str] | no | -- | DHCP interface slot ids |
| `regdhcp / regdhcpstatic / dhcpfirst / strict_order / domain_needed / no_private_reverse / no_resolv / log_queries / no_hosts / dnssec / add_subnet / strip_subnet / no_ident` | bool | no | -- | Toggles |
| `regdhcpdomain / dns_forward_max / cache_size / local_ttl / add_mac` | str | no | -- |  |
| `state` | str | no | present | Only `present` |

### opnsense_dnsmasq_service

Control Dnsmasq (default `stopped` — free 67/547 for Kea).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `state` | str | no | stopped | `running`, `stopped` or `reconfigured` |

### opnsense_ids_settings

Manage the Suricata `general` block (singleton). `mode: pcap` = IDS (alert only); `netmap`/`divert` = inline IPS. A seeded FW stores `interfaces=wan` (not a valid slot on our seeds) — set `interfaces` here BEFORE toggling rulesets or every IDS save fails validation.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `enabled` | bool | no | -- | Enable Suricata |
| `mode` | str | no | -- | `pcap`, `netmap`, `divert` |
| `interfaces` | list[str] | no | -- | Interface slot ids |
| `homenet` | list[str] | no | -- | HOME_NET networks |
| `syslog / syslog_eve` | bool | no | -- | Alerts / EVE JSON to syslog (Loki path) |
| `eve_log` | list[str] | no | -- | `http`, `tls` (API `eveLog`) |
| `log_payload / promisc / divert_listeners` | bool | no | -- |  |
| `alert_logrotate / alert_save_logs / mpm_algo / verbosity / default_packet_size` | str | no | -- | Advanced (API CamelCase fields) |
| `state` | str | no | present | Only `present` |

### opnsense_ids_ruleset

Enable/disable rulesets from the device catalogue (68 on 26.7.3: 48 ET Open `emerging-*.rules`, abuse.ch ×5, OPNsense app-detect). Only drifted sets are toggled; fetch the rules with `opnsense_ids_service: rules_updated`.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `rulesets` | dict | no | -- | filename → enabled |
| `enable_prefix` | list[str] | no | -- | Enable every ruleset starting with a prefix (`emerging-` = all ET Open) |
| `disable_others` | bool | no | false | Disable every ruleset not covered above |
| `apply` | bool | no | true | Reconfigure after toggling |

### opnsense_ids_service

Control Suricata; `rules_updated` runs `updateRules` (long-running, always changed).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `state` | str | no | running | `running`, `stopped`, `reconfigured`, `rules_updated` |

### opnsense_mdnsrepeater_settings

Manage the os-mdns-repeater settings (singleton). Needs at least two interfaces.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `enabled` | bool | no | -- | Enable |
| `interfaces` | list[str] | no | -- | Interface slot ids (>= 2) |
| `blocklist` | list[str] | no | -- | Networks to drop |
| `enablecarp` | bool | no | -- | Follow CARP |
| `state` | str | no | present | Only `present` |

### opnsense_mdnsrepeater_service

Control the mDNS repeater.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `state` | str | no | running | `running`, `stopped` or `reconfigured` |

### opnsense_ub_diagnostics

Query Unbound DNS resolver diagnostics (read-only, no `state` param).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `info_type` | str | yes | -- | `stats` or `dnsbl` |

**Returns**: `data` dict with resolver statistics or DNSBL information.

---

## DHCP / Kea

### opnsense_kea4_subnet

Manage Kea DHCPv4 subnets.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `subnet` | str | yes | -- | Subnet in CIDR notation (e.g. `10.0.0.0/24`) |
| `pools` | str | no | "" | Address pool ranges |
| `next_server` | str | no | "" | TFTP / PXE next-server |
| `description` | str | no | "" | Subnet description |
| `option_data` | dict | no | -- | DHCP options (routers, domain_name_servers, domain_search, domain_name, ntp_servers, time_servers, static_routes, classless_static_route, tftp_server_name, boot_file_name) — diffed sub-key by sub-key |
| `match_client_id` | bool | no | -- | API `match-client-id` |
| `state` | str | no | present | `present` or `absent` |

### opnsense_kea4_reservation

Manage Kea DHCPv4 static reservations.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ip_address` | str | yes | -- | Reserved IP address |
| `hw_address` | str | yes | -- | Client MAC address |
| `hostname` | str | no | "" | Client hostname |
| `description` | str | no | "" | Reservation description |
| `state` | str | no | present | `present` or `absent` |

### opnsense_kea4_peer

Manage Kea DHCPv4 HA peers.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | Peer name (unique) |
| `role` | str | no | primary | `primary` or `standby` |
| `url` | str | yes | -- | Peer URL |
| `state` | str | no | present | `present` or `absent` |

### opnsense_kea6_subnet

Manage Kea DHCPv6 subnets.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `subnet` | str | yes | -- | Subnet in CIDR notation |
| `interface` | str | yes | -- | Interface (required by Kea DHCPv6) |
| `description` | str | no | "" | Subnet description |
| `state` | str | no | present | `present` or `absent` |

### opnsense_kea6_reservation

Manage Kea DHCPv6 static reservations.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ip_address` | str | yes | -- | Reserved IPv6 address |
| `duid` | str | yes | -- | Client DUID |
| `hostname` | str | no | "" | Client hostname |
| `description` | str | no | "" | Reservation description |
| `state` | str | no | present | `present` or `absent` |

---

## WireGuard

### opnsense_wg_server

Manage WireGuard server (tunnel) instances.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | Server name (unique) |
| `enabled` | bool | no | true | Enable the tunnel |
| `listen_port` | int | no | -- | Listen port (maps to API field `port`) |
| `mtu` | int | no | -- | Tunnel MTU |
| `tunneladdress` | str | no | "" | Tunnel IP address(es) |
| `dns` | str | no | "" | DNS servers |
| `disableroutes` | bool | no | false | Disable automatic routes |
| `gateway` | str | no | "" | Gateway for tunnel |
| `peers` | str | no | "" | Comma-separated peer UUIDs |
| `state` | str | no | present | `present` or `absent` |

### opnsense_wg_client

Manage WireGuard client (peer) entries.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | Client name (unique) |
| `enabled` | bool | no | true | Enable the peer |
| `pubkey` | str | no | "" | Peer public key (`no_log: true`) |
| `psk` | str | no | "" | Pre-shared key (`no_log: true`) |
| `tunneladdress` | str | no | "" | Allowed IPs |
| `serveraddress` | str | no | "" | Endpoint address |
| `serverport` | int | no | -- | Endpoint port |
| `keepalive` | int | no | 0 | Persistent keepalive interval |
| `endpoint` | str | no | "" | Endpoint override |
| `state` | str | no | present | `present` or `absent` |

---

## IPsec

### opnsense_ipsec_conn

Manage IPsec IKE connections.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | -- | Connection description (match key) |
| `enabled` | bool | no | true | Enable the connection |
| `version` | str | no | "" | IKE version |
| `aggressive` | bool | no | false | Aggressive mode |
| `mobike` | bool | no | false | MOBIKE support |
| `reauth_time` | str | no | "" | Re-authentication time |
| `rekey_time` | str | no | "" | Re-key time |
| `dpd_delay` | str | no | "" | DPD delay |
| `dpd_timeout` | str | no | "" | DPD timeout |
| `keyingtries` | str | no | "" | Keying tries |
| `state` | str | no | present | `present` or `absent` |

### opnsense_ipsec_child

Manage IPsec child SAs.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | -- | Child SA description (match key) |
| `enabled` | bool | no | true | Enable the child SA |
| `connection` | str | no | "" | Parent connection UUID |
| `mode` | str | no | "" | SA mode (tunnel, transport) |
| `policies` | bool | no | true | Install policies |
| `rekey_time` | str | no | "" | Re-key time |
| `sha256_96` | bool | no | false | SHA-256 96-bit truncation |
| `state` | str | no | present | `present` or `absent` |

### opnsense_ipsec_local

Manage IPsec local authentication.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | -- | Local auth description (match key) |
| `enabled` | bool | no | true | Enable |
| `connection` | str | no | "" | Parent connection UUID |
| `auth` | str | no | "" | Auth method |
| `id` | str | no | "" | Local identity |
| `eap_id` | str | no | "" | EAP identity |
| `round` | str | no | "" | Auth round |
| `state` | str | no | present | `present` or `absent` |

### opnsense_ipsec_remote

Manage IPsec remote authentication.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | -- | Remote auth description (match key) |
| `enabled` | bool | no | true | Enable |
| `connection` | str | no | "" | Parent connection UUID |
| `auth` | str | no | "" | Auth method |
| `id` | str | no | "" | Remote identity |
| `eap_id` | str | no | "" | EAP identity |
| `round` | str | no | "" | Auth round |
| `state` | str | no | present | `present` or `absent` |

### opnsense_ipsec_psk

Manage IPsec pre-shared keys.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | -- | PSK description (match key) |
| `ident` | str | no | "" | Local identity |
| `remote_ident` | str | no | "" | Remote identity |
| `keyType` | str | no | "" | Key type |
| `Key` | str | no | "" | Pre-shared key value (`no_log: true`) |
| `state` | str | no | present | `present` or `absent` |

### opnsense_ipsec_keypair

Manage IPsec key pairs.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | Key pair name (unique) |
| `keyType` | str | no | "" | Key type |
| `publicKey` | str | no | "" | Public key |
| `privateKey` | str | no | "" | Private key (`no_log: true`) |
| `state` | str | no | present | `present` or `absent` |

### opnsense_ipsec_pool

Manage IPsec address pools.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | -- | Pool name (unique) |
| `enabled` | bool | no | true | Enable the pool |
| `addrs` | str | no | "" | Address range(s) |
| `dns` | str | no | "" | DNS servers for pool |
| `state` | str | no | present | `present` or `absent` |

### opnsense_ipsec_vti

Manage IPsec virtual tunnel interfaces.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | -- | VTI description (match key) |
| `enabled` | bool | no | true | Enable the VTI |
| `reqid` | str | no | "" | Request ID |
| `local` | str | no | "" | Local address |
| `remote` | str | no | "" | Remote address |
| `tunnel_local` | str | no | "" | Tunnel local address |
| `tunnel_remote` | str | no | "" | Tunnel remote address |
| `state` | str | no | present | `present` or `absent` |

---

## OpenVPN

### opnsense_ovpn_instance

Manage OpenVPN server or client instances.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | -- | Instance description (match key) |
| `enabled` | bool | no | true | Enable the instance |
| `role` | str | no | server | `server` or `client` |
| `dev_type` | str | no | "" | Device type (tun, tap) |
| `proto` | str | no | "" | Protocol (UDP, TCP) |
| `listen_port` | int | no | -- | Listen port (maps to API field `port`) |
| `server` | str | no | "" | Server network |
| `cert` | str | no | "" | Certificate refid |
| `ca` | str | no | "" | CA refid |
| `local` | str | no | "" | Local address |
| `remote` | str | no | "" | Remote address |
| `keepalive_interval` | str | no | "" | Keepalive interval |
| `keepalive_timeout` | str | no | "" | Keepalive timeout |
| `tun_mtu` | str | no | "" | Tunnel MTU |
| `maxclients` | str | no | "" | Maximum clients |
| `username` | str | no | "" | Username |
| `password` | str | no | "" | Password (`no_log: true`) |
| `state` | str | no | present | `present` or `absent` |

---

## Shaper

### opnsense_ts_pipe

Manage traffic shaper bandwidth pipes.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | -- | Pipe description (match key) |
| `bandwidth` | int | yes | -- | Bandwidth value |
| `bandwidthMetric` | str | no | Mbit | `bit`, `Kbit`, `Mbit`, or `Gbit` |
| `enabled` | bool | no | true | Enable the pipe |
| `delay` | str | no | "" | Delay in milliseconds |
| `mask` | str | no | none | `none`, `src-ip`, `dst-ip`, `src-ip6`, `dst-ip6` |
| `scheduler` | str | no | "" | Scheduler type |
| `state` | str | no | present | `present` or `absent` |

### opnsense_ts_queue

Manage traffic shaper queues.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | -- | Queue description (match key) |
| `weight` | int | no | 50 | Queue weight (1-100) |
| `enabled` | bool | no | true | Enable the queue |
| `mask` | str | no | none | `none`, `src-ip`, `dst-ip`, `src-ip6`, `dst-ip6` |
| `state` | str | no | present | `present` or `absent` |

### opnsense_ts_rule

Manage traffic shaper rules.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | -- | Rule description (match key) |
| `interface` | str | yes | -- | Interface |
| `proto` | str | no | ip | `ip`, `ip4`, `ip6`, `udp`, or `tcp` |
| `direction` | str | no | "" | `""`, `in`, or `out` |
| `enabled` | bool | no | true | Enable the rule |
| `sequence` | int | no | -- | Rule sequence number |
| `src_port` | str | no | "" | Source port (numeric, range, or alias) |
| `dst_port` | str | no | "" | Destination port (numeric, range, or alias) |
| `state` | str | no | present | `present` or `absent` |

---

## Trust / PKI

### opnsense_trust_ca

Manage certificate authorities (internal or imported).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `descr` | str | yes | -- | CA description (match key) |
| `action` | str | no | internal | `existing` (import) or `internal` (generate) |
| `key_type` | str | no | "" | Key type (e.g. RSA, EC) |
| `digest` | str | no | "" | Digest algorithm |
| `lifetime` | int | no | -- | Certificate lifetime in days |
| `commonname` | str | no | "" | Common name |
| `country` | str | no | "" | Country code |
| `province` | str | no | "" | State / province |
| `city` | str | no | "" | City |
| `organization` | str | no | "" | Organization |
| `email` | str | no | "" | Email |
| `crt_payload` | str | no | "" | PEM certificate (for import) |
| `prv_payload` | str | no | "" | PEM private key (`no_log: true`) |
| `caref` | str | no | "" | Parent CA reference ID |
| `state` | str | no | present | `present` or `absent` |

### opnsense_trust_cert

Manage certificates (internal, external, or imported).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `descr` | str | yes | -- | Certificate description (match key) |
| `caref` | str | no | "" | Signing CA reference ID |
| `action` | str | no | internal | `internal`, `external`, or `existing` |
| `key_type` | str | no | "" | Key type |
| `digest` | str | no | "" | Digest algorithm |
| `cert_type` | str | no | server_cert | `usr_cert` or `server_cert` |
| `lifetime` | int | no | -- | Certificate lifetime in days |
| `commonname` | str | no | "" | Common name |
| `altnames_dns` | str | no | "" | SAN DNS names (comma-separated) |
| `altnames_ip` | str | no | "" | SAN IP addresses (comma-separated) |
| `country` | str | no | "" | Country code |
| `province` | str | no | "" | State / province |
| `city` | str | no | "" | City |
| `organization` | str | no | "" | Organization |
| `email` | str | no | "" | Email |
| `crt_payload` | str | no | "" | PEM certificate (for import) |
| `prv_payload` | str | no | "" | PEM private key (`no_log: true`) |
| `csr_payload` | str | no | "" | PEM CSR (for external signing) |
| `state` | str | no | present | `present` or `absent` |

---

## Services

### opnsense_cp_zone

Manage Captive Portal zones.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | -- | Zone description (match key) |
| `enabled` | bool | no | true | Enable the zone |
| `interfaces` | str | no | "" | Comma-separated interfaces |
| `authservers` | str | no | "" | Auth server(s) |
| `idletimeout` | int | no | 0 | Idle timeout in minutes |
| `hardtimeout` | int | no | 0 | Hard timeout in minutes |
| `concurrentlogins` | bool | no | true | Allow concurrent logins |
| `certificate` | str | no | "" | Certificate refid |
| `servername` | str | no | "" | Server name |
| `state` | str | no | present | `present` or `absent` |

### opnsense_cron_job

Manage cron jobs.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | -- | Job description (match key) |
| `enabled` | bool | no | true | Enable the job |
| `minutes` | str | no | 0 | Cron minutes |
| `hours` | str | no | 0 | Cron hours |
| `days` | str | no | * | Cron day of month |
| `months` | str | no | * | Cron month |
| `weekdays` | str | no | * | Cron day of week |
| `command` | str | no | "" | Command to run |
| `who` | str | no | root | User to run as |
| `parameters` | str | no | "" | Command parameters |
| `state` | str | no | present | `present` or `absent` |

### opnsense_ddns_account

Manage dynamic DNS accounts.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | -- | Account description (match key) |
| `enabled` | bool | no | true | Enable the account |
| `service` | str | no | "" | DDNS provider service type |
| `protocol` | str | no | "" | Protocol |
| `server` | str | no | "" | Server override |
| `username` | str | no | "" | Account username |
| `password` | str | no | "" | Account password (`no_log: true`) |
| `hostnames` | str | yes | -- | Hostnames to update |
| `checkip` | str | yes | -- | Check IP method |
| `interface` | str | no | "" | Interface for IP detection |
| `state` | str | no | present | `present` or `absent` |

### opnsense_syslog_dest

Manage remote syslog destinations.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | -- | Destination description (match key) |
| `enabled` | bool | no | true | Enable the destination |
| `transport` | str | no | udp4 | `udp4`, `tcp4`, `udp6`, `tcp6`, `tls4`, or `tls6` |
| `hostname` | str | yes | -- | Remote syslog server hostname |
| `syslog_port` | str | no | 514 | Remote port (maps to API field `port`) |
| `rfc5424` | bool | no | false | Use RFC 5424 format |
| `certificate` | str | no | "" | TLS certificate refid |
| `state` | str | no | present | `present` or `absent` |

---

## Return Values (all modules)

| Key | Type | Description |
|-----|------|-------------|
| `changed` | bool | Whether any changes were made |
| `action` | str | `created`, `updated`, `deleted`, or `noop` |
| `uuid` | str | Resource UUID (when available) |
| `diff` | dict | Before/after state (when changed) |
