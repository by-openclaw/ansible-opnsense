# Modules

> All modules are thin wrappers around lib-opnsense managers.
> They translate Ansible parameters into `ensure()` calls and return structured results.

## Connection Parameters (shared)

All modules accept these connection parameters:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `host` | str | yes | — | OPNsense hostname or IP |
| `key` | str | yes | — | API key (`no_log: true`) |
| `secret` | str | yes | — | API secret (`no_log: true`) |
| `port` | int | no | 443 | HTTPS port |
| `verify_ssl` | bool | no | false | Verify TLS certificate |

## opnsense_auth_user

Manage local users: create, update, delete with idempotency.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | — | Username (unique) |
| `email` | str | no | "" | Email address |
| `description` | str | no | "" | User description |
| `password` | str | no | — | Password (`no_log: true`) |
| `group_memberships` | str | no | "" | Comma-separated GIDs |
| `disabled` | bool | no | false | Disable account |
| `state` | str | no | present | `present` or `absent` |

## opnsense_auth_group

Manage local groups.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | — | Group name (unique) |
| `description` | str | no | "" | Group description |
| `state` | str | no | present | `present` or `absent` |

## opnsense_auth_priv

Assign or unassign privileges to users or groups.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `priv_id` | str | yes | — | Privilege ID (e.g. `page-all`) |
| `target_type` | str | yes | — | `user` or `group` |
| `target_name` | str | yes | — | Name of the user or group |
| `state` | str | no | present | `present` (assign) or `absent` (unassign) |

## opnsense_auth_api_key

Create or delete API keys for users.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `username` | str | yes | — | Username to manage keys for |
| `state` | str | no | present | `present` (create) or `absent` (delete all) |

**Returns** on create: `api_key` and `api_secret` (shown once, `no_log: true`).

## opnsense_fw_alias

Manage firewall aliases (hosts, networks, ports, URLs).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | — | Alias name (unique) |
| `type` | str | no | host | Alias type (host, network, port, url, etc.) |
| `content` | str | no | "" | Content — IPs, networks, ports (newline-separated) |
| `description` | str | no | "" | Alias description |
| `enabled` | bool | no | true | Enable the alias |
| `proto` | str | no | "" | Protocol filter (IPv4, IPv6) |
| `state` | str | no | present | `present` or `absent` |

## opnsense_fw_filter

Manage firewall filter rules (pass/block/reject).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | — | Rule description (used as match key) |
| `action` | str | no | pass | `pass`, `block`, or `reject` |
| `interface` | str | no | lan | Interface |
| `direction` | str | no | in | `in`, `out`, or `any` |
| `ipprotocol` | str | no | inet | `inet`, `inet6`, `inet46` |
| `protocol` | str | no | any | Transport protocol (TCP, UDP, etc.) |
| `source_net` | str | no | any | Source network or alias |
| `source_port` | str | no | "" | Source port |
| `destination_net` | str | no | any | Destination network or alias |
| `destination_port` | str | no | "" | Destination port |
| `enabled` | bool | no | true | Enable the rule |
| `log` | bool | no | false | Log matching packets |
| `state` | str | no | present | `present` or `absent` |

## opnsense_fw_dnat

Manage D-NAT / port forward rules. **Requires OPNsense >= 26.1.**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `descr` | str | yes | — | Rule description (match key — note: `descr` not `description`) |
| `interface` | str | no | wan | Interface |
| `ipprotocol` | str | no | inet | IP version |
| `protocol` | str | no | tcp | Transport protocol |
| `target` | str | yes | — | Internal target IP |
| `local_port` | str | no | "" | Internal target port |
| `disabled` | bool | no | false | Disable the rule |
| `log` | bool | no | false | Log matching packets |
| `state` | str | no | present | `present` or `absent` |

## opnsense_fw_source_nat

Manage source NAT (outbound NAT / masquerade) rules.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | str | yes | — | Rule description (match key) |
| `interface` | str | no | wan | Interface |
| `ipprotocol` | str | no | inet | `inet` or `inet6` |
| `protocol` | str | no | any | Transport protocol |
| `source_net` | str | no | any | Source network |
| `destination_net` | str | no | any | Destination network |
| `target` | str | no | wanip | NAT target address |
| `enabled` | bool | no | true | Enable the rule |
| `log` | bool | no | false | Log matching packets |
| `state` | str | no | present | `present` or `absent` |

## Return Values (all modules)

| Key | Type | Description |
|-----|------|-------------|
| `changed` | bool | Whether any changes were made |
| `action` | str | `created`, `updated`, `deleted`, or `noop` |
| `uuid` | str | Resource UUID (when available) |
| `diff` | dict | Before/after state (when changed) |
