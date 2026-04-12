# AGENTS.md -- ansible-opnsense

> **Rules:** See [OPERATING-STANDARD.md](~/.openclaw/workspace/OPERATING-STANDARD.md) for all platform rules.

Ansible collection wrapping lib-opnsense -- 54 thin modules across 12 scopes for full OPNsense automation with ensure() idempotency.

## Always Read First

Before touching anything in this repo:

1. [`README.md`](README.md) -- collection overview, usage, modules
2. [`CLAUDE.md`](CLAUDE.md) -- agent-specific constraints, hard rules
3. [`galaxy.yml`](galaxy.yml) -- collection metadata
4. [`plugins/modules/`](plugins/modules/) -- module source
5. `/home/by-systems/repos/lib-opnsense/CLAUDE.md` -- library constraints and API gotchas
6. `/home/by-systems/repos/lib-opnsense/src/opnsense/` -- library source (understand what you are wrapping)

## Coding & Commit Standards

- **Module pattern:** thin wrapper -- instantiate client, create manager, call ensure(), return result
- **Naming:** `opnsense_{domain}_{entity}.py` (ADR-0030)
- **DOCUMENTATION/EXAMPLES/RETURN:** required docstrings on every module
- **Linting:** `ansible-lint` -- must be clean before commit
- **Branch naming:** `feat/{issue-id}-{description}` or `fix/{issue-id}-{description}`
- **check_mode:** all modules must support check_mode
- **No API logic in modules** -- all API calls go through lib-opnsense

## What NOT To Do

> Also read `CLAUDE.md` HARD RULES -- architectural decisions enforced there. AGENTS.md and CLAUDE.md are both authoritative. When in doubt, CLAUDE.md wins.

- Do NOT implement API calls in modules -- use lib-opnsense
- Do NOT publish to Galaxy without explicit instruction from @yboujraf
- Do NOT hardcode credentials in source, tests, or playbooks
- Do NOT run integration playbooks without OPN_HOST/OPN_KEY/OPN_SECRET set

## Test Device

**OPNsense 26.1** at `opnsense.example.com` (port 443).

### `svc-rune` -- API executor
- API key stored in `.env` (gitignored)
- Full API access for integration tests
- Environment variables: `OPN_HOST`, `OPN_KEY`, `OPN_SECRET`

## GitHub Repo

<https://github.com/by-openclaw/ansible-opnsense>

## Agent: Rune

Maintained by Rune (DevOps familiar) for the BY-SYSTEMS PoC platform.
Owner: @yboujraf

---

## Project Stats

> Auto-updated on every release. Last updated: 2026-04-11

| Metric | Value |
|---|---|
| Version | 0.2.0 (scope expansion) |
| Modules | 54 |
| Roles | 11 |
| Playbooks | 23 |
| Integration tests | 30 |
| CI workflows | 3 |
| ansible-lint | 0 failures (production profile) |
