# AGENTS.md -- ansible-opnsense

Ansible collection wrapping lib-opnsense -- thin modules for OPNsense user/group management with ensure() idempotency.

## Always Read First

Before touching anything in this repo:

1. [`README.md`](README.md) -- collection overview, usage, modules
2. [`CLAUDE.md`](CLAUDE.md) -- agent-specific constraints, hard rules
3. [`galaxy.yml`](galaxy.yml) -- collection metadata
4. [`plugins/modules/`](plugins/modules/) -- module source

## Mandatory reading before acting

Before writing, editing, or reviewing any file in this repo, read:

### doc-platform-core repo:
1. `/home/by-systems/.openclaw/workspace/repos/doc-platform-core/docs/standards/` -- all standards files
2. `/home/by-systems/.openclaw/workspace/repos/doc-platform-core/docs/adr/` -- all Accepted ADRs

### lib-opnsense repo:
1. `/home/by-systems/.openclaw/workspace/repos/lib-opnsense/CLAUDE.md` -- library constraints and API gotchas
2. `/home/by-systems/.openclaw/workspace/repos/lib-opnsense/src/opnsense/` -- library source (understand what you are wrapping)

### Rules:
- Do NOT infer. Do NOT invent policy. If a standard or ADR covers it -- follow it.
- If you would override a standard -- flag it with `[OVERRIDE REQUIRED]`, do NOT do it silently.
- Cross-ADR dependencies are FORBIDDEN. Each ADR is self-contained.

## Coding & Commit Standards

- **Module pattern:** thin wrapper -- instantiate client, create manager, call ensure(), return result
- **Naming:** `opnsense_{domain}_{entity}.py` (ADR-0030)
- **DOCUMENTATION/EXAMPLES/RETURN:** required docstrings on every module
- **Linting:** `ansible-lint` -- must be clean before commit
- **Conventional Commits** -- `type(scope): description`
  - Types: `feat`, `fix`, `docs`, `test`, `ci`, `refactor`, `chore`
  - Examples:
    - `feat(auth): add opnsense_auth_priv module`
    - `fix(auth_user): handle missing email field`
    - `docs(readme): update module table`
- **Branch naming:** `feat/{issue-id}-{description}` or `fix/{issue-id}-{description}`
- **check_mode:** all modules must support check_mode
- **No API logic in modules** -- all API calls go through lib-opnsense

## Project Health Rules (mandatory)

- **Test fails -> open issue immediately.** Never fix silently. Issue first -> fix -> close with comment + commit ref.
- **Issue closed = CI green + specific test covers the fix.** No exceptions.
- **CI failure on main** that isn't already tracked -> create a GitHub issue before anything else.
- **Every open issue** has a label, is on the Project board, has a linked commit or PR when closed.
- README reflects actual state -- not aspirational. Update after every release.
- AGENTS.md + CLAUDE.md updated after every non-trivial change.

## What NOT To Do

> Also read `CLAUDE.md` HARD RULES -- architectural decisions enforced there. AGENTS.md and CLAUDE.md are both authoritative. When in doubt, CLAUDE.md wins.

- Do NOT implement API calls in modules -- use lib-opnsense
- Do NOT publish to Galaxy without explicit instruction from @yboujraf
- Do NOT hardcode credentials in source, tests, or playbooks
- Do NOT run integration playbooks without OPN_HOST/OPN_KEY/OPN_SECRET set

## Test Device

**OPNsense 25.1.12** at `10.6.224.106` (port 443).

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

> Auto-updated on every release. Last updated: 2026-04-04

| Metric | Value |
|---|---|
| Version | v0.1.0 |
| Tagged releases | 0 |
| Modules | 2 (auth_user, auth_group) |
| Integration tests | Pending |
| CI workflows | Pending |
| ansible-lint | Pending |
