# Error Handling

## How Errors Flow

```
OPNsense API → lib-opnsense client → manager (try/except/log/re-raise) → Ansible module (try/except/finally → fail_json)
```

## Exception → fail_json Mapping

| lib-opnsense Exception | Ansible fail_json msg | HTTP |
|------------------------|----------------------|------|
| `OpnsenseAuthError` | "Authentication failed... Check API key and secret." | 401 |
| `OpnsenseValidationError` | "Validation failed..." + `validations` dict | 400 |
| `OpnsenseEndpointMissingError` | "Endpoint not found... Check OPNsense version >= 26.1." | 404 |
| `OpnsenseTimeoutError` | "Request timed out..." | — |
| `OpnsenseConnectionError` | "Connection failed... Check host, port, and network." | — |
| `OpnsenseServerError` | "OPNsense server error... Retry or check device health." | 500 |

## finally Block

Every module call guarantees `client.close()` in `finally` — no connection leaks even on failure.

## Logging

Structured JSON logs written to:
- **Production**: `/var/log/opnsense/ansible-opnsense.log`
- **Fallback**: `~/.opnsense/logs/ansible-opnsense.log`

Log level follows Ansible verbosity: `-vv` → DEBUG, otherwise INFO.

Format: Loki-compatible JSON, one line per event.
