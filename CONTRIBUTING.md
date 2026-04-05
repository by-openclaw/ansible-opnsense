# Contributing to ansible-opnsense

## Development setup

```bash
git clone https://github.com/by-openclaw/ansible-opnsense.git
cd ansible-opnsense

# Install the Python library dependency
pip install git+https://github.com/by-openclaw/lib-opnsense.git

# Install linting tools
pip install ansible-lint

# Set OPNsense credentials for integration testing
cp .env.example .env
# Edit .env with your OPNsense API key/secret
```

## Linting

```bash
ansible-lint plugins/
```

## Integration testing

Requires a live OPNsense device with API access.

```bash
export OPN_HOST=10.6.224.106
export OPN_KEY=your-api-key
export OPN_SECRET=your-api-secret

# Dry run
ansible-playbook playbooks/playbook_auth.yml --check

# Live run
ansible-playbook playbooks/playbook_auth.yml
```

## Adding a new module

1. Add the manager to lib-opnsense first (all API logic lives there).
2. Create `plugins/modules/opnsense_{domain}_{entity}.py` following the existing pattern.
3. Include `DOCUMENTATION`, `EXAMPLES`, and `RETURN` docstrings.
4. Support `check_mode`.
5. Update `README.md` module table.
6. Update `CLAUDE.md` current state table.
7. Add tasks to `playbooks/playbook_auth.yml` (or create a new playbook).

## Commit standard

All commits MUST follow Conventional Commits format:

```
<type>[optional scope]: <description>
```

| Type | When |
|---|---|
| `feat:` | New module or feature |
| `fix:` | Bug fix |
| `docs:` | Documentation only |
| `chore:` | Maintenance, CI, refactor |

## PR checklist

- [ ] Module has DOCUMENTATION, EXAMPLES, RETURN docstrings
- [ ] check_mode supported
- [ ] ansible-lint clean
- [ ] No credentials in committed files
- [ ] CHANGELOG entry added
- [ ] CLAUDE.md updated if state changed

## Release process

Never edit version numbers manually.

```
push commits with conventional messages -> release-please opens PR -> merge it -> done
```
