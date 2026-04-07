## Summary

<!-- One sentence: what changed and why. -->

Closes #

## Type

- [ ] feat — new feature
- [ ] fix — bug fix
- [ ] docs — documentation only
- [ ] chore — maintenance, refactor, CI
- [ ] security — security fix or hardening

## Files changed

<!-- List every file touched. One row per file. -->

| File | Type | Change |
|------|------|--------|
| `plugins/modules/opnsense_example.py` | new | Ansible module (N lines) |
| `roles/example/tasks/main.yml` | new | Role tasks |
| `playbooks/playbook_example_e2e.yml` | new | E2E test playbook |
| `docs/modules.md` | update | Added module documentation |

## Modules / roles covered

<!-- For each Ansible module or role this PR touches. -->

| Module / Role | Manager (lib) | Endpoints | Tested |
|--------------|--------------|-----------|--------|
| `opnsense_example` | ExampleManager | search, get, add, set, del | E2E playbook |
| `roles/example` | — | — | E2E playbook |

## Test results

<!-- E2E playbook results. -->

| Playbook | Tasks | Changed | Failed | Ignored |
|----------|-------|---------|--------|---------|
| `playbook_example_e2e.yml` | 0 | 0 | 0 | 0 |

| Check | Tool | Status |
|-------|------|--------|
| Lint | ansible-lint | clean |
| Sanity | ansible-test sanity | clean |
| CI | Python 3.10-3.13 | all pass |

## Safety

<!-- What is safe to touch on the live device? What is read-only? -->

- **READ-ONLY:**
- **CRUD safe (inttest- prefix):**
- **DISABLED only:**

## How to review

1. Read module code — verify `opn_argument_spec` + `run_module` pattern
2. Read role tasks — verify variable names match `defaults/main.yml`
3. Read E2E playbook — verify create, noop, error handling, cleanup phases
4. Check: no hardcoded IPs, no real domains, inttest- prefix everywhere
5. Check: `docs/modules.md` documents all new modules

## Checklist

### Quality
- [ ] Lint clean (`ansible-lint`)
- [ ] Sanity clean (Python 3.10-3.13)
- [ ] E2E playbook tested against live device
- [ ] Log file shows correct levels (error=error, info=info)

### Security
- [ ] No secrets, tokens, or passwords in committed files
- [ ] All credential params marked `no_log: true`

### Docs
- [ ] CHANGELOG entry added (if user-facing change)
- [ ] CLAUDE.md updated (if repo state changed)
- [ ] `docs/modules.md` updated (if module added)

### ADR compliance
- [ ] Module uses `opn_argument_spec` + `run_module` (ADR-0030)
- [ ] Module supports `check_mode` (ADR-0029)
- [ ] Error handling: typed exceptions mapped to `fail_json` (ADR-0029)

## Review

- [ ] @yboujraf approved

<!--
Merge rules (ADR-0019):
- Agents open PRs, never merge
- @yboujraf is sole merge authority
- No force-push to main — ever
-->
