> **Mandatory -- read before any work:**
> 1. `workspace/OPERATING-STANDARD.md` -- platform rules, quality gates, compliance
> 2. This file -- repo-specific context

# CLAUDE.md -- ansible-opnsense

> **Scope:** `ansible` | **Component:** `opnsense`
> **GitHub:** `by-openclaw/ansible-opnsense`
> **Layer:** Layer 0 -- Edge & Routing

AI agent context. Read before touching any file.

---

## What This Repo Does

Ansible collection (`by_systems.opnsense`) providing thin wrapper modules around the lib-opnsense Python library.
Modules translate Ansible parameters into `ensure()` calls on lib-opnsense managers and return structured results.

**NOT for:** implementing API calls, retry logic, or business logic. All of that lives in lib-opnsense.

---

## HARD RULES -- Non-negotiable. Read before touching any file.

These are architectural decisions. They are NOT suggestions. Do not override them.

### Modules are thin wrappers (ADR-0030)
- **NEVER implement API calls in modules directly.** All logic lives in lib-opnsense.
- Modules instantiate an `OpnsenseClient`, create a manager, call `ensure()`, and return the result.
- If you need new API functionality, add it to lib-opnsense first, then wrap it here.

### Naming convention (ADR-0030)
- Module files are named `opnsense_{domain}_{entity}.py` (e.g. `opnsense_auth_user.py`).
- FQCN: `by_systems.opnsense.opnsense_{domain}_{entity}`.

### Dependency: lib-opnsense must be pip-installed
- lib-opnsense is not bundled. It must be installed via pip on the Ansible control node.
- Modules import from `opnsense.client` and `opnsense.managers.*` at runtime.

### Credential handling
- Credentials are passed as module parameters (`host`, `key`, `secret`).
- `key` and `secret` are marked `no_log: true` in argument_spec.
- Never log, print, or include credentials in return values.

### Commit and version discipline
- All commits MUST follow Conventional Commits format.
- Release Please is the canonical release path.
- Never manually edit version strings in galaxy.yml.

---

## Current State (v0.1.0 -- scaffold)

| Component | Status |
|---|---|
| opnsense_auth_user module | Scaffold |
| opnsense_auth_group module | Scaffold |
| galaxy.yml collection metadata | Done |
| CI: ansible-lint | Pending |
| ansible-test sanity | Pending |
| Integration tests (live device) | Pending |
| Dev container (.devcontainer/) | Pending |

---

## Key Files

| File | Why |
|---|---|
| `galaxy.yml` | Collection metadata -- namespace, version, dependencies |
| `plugins/modules/opnsense_auth_user.py` | Local user CRUD module |
| `plugins/modules/opnsense_auth_group.py` | Local group CRUD module |
| `playbooks/playbook_auth.yml` | Integration test playbook |
| `README.md` | Install, usage, module reference |
| `CHANGELOG.md` | Semantic versioning history |

---

## Constraints

- Never commit OPNsense credentials or API keys
- All modules must support `check_mode`
- All modules must return `changed`, `action`, `uuid`, `diff`
- `ansible-lint` must pass before any merge to `main`
- Breaking changes = MAJOR version bump + migration note in CHANGELOG

---

## Cross-repo References

- lib-opnsense: `by-openclaw/lib-opnsense` -- the Python library this collection wraps
- ADR-0029: Async library standard -- `doc-platform-core/docs/adr/`
- ADR-0030: OPNsense API automation standard -- `doc-platform-core/docs/adr/`
- Naming convention: `doc-platform-core/docs/adr/0010-naming-and-identity-convention.md`

---

## Related

- Platform charter: `doc-platform-core/docs/adr/0006-platform-charter.md`
- GitHub Issues: <https://github.com/by-openclaw/ansible-opnsense/issues>
