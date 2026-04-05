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

## Return Values (all modules)

| Key | Type | Description |
|-----|------|-------------|
| `changed` | bool | Whether any changes were made |
| `action` | str | `created`, `updated`, `deleted`, or `noop` |
| `uuid` | str | Resource UUID (when available) |
| `diff` | dict | Before/after state (when changed) |
