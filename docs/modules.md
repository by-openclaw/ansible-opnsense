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
