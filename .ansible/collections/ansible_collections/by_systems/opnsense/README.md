# BY-SYSTEMS OPNsense Ansible Collection

> **`by_systems.opnsense`** — Ansible collection for OPNsense firewall automation.
> Thin wrapper modules around [lib-opnsense](https://github.com/by-openclaw/lib-opnsense).
> Requires OPNsense **>= 26.1**.

## Requirements

- Python 3.10+
- Ansible 2.15+
- lib-opnsense >= 1.0.0 (`pip install opnsense`)

## Installation

```bash
# Install the Python library dependency
pip install git+https://github.com/by-openclaw/lib-opnsense.git

# Install the collection from local checkout
ansible-galaxy collection install /path/to/ansible-opnsense

# Or build and install
cd ansible-opnsense
ansible-galaxy collection build
ansible-galaxy collection install by_systems-opnsense-0.1.0.tar.gz
```

## Collection Structure

```
ansible-opnsense/
├── galaxy.yml                          # Collection metadata (namespace: by_systems)
├── plugins/
│   ├── modules/
│   │   ├── opnsense_auth_user.py       # CRUD local users
│   │   ├── opnsense_auth_group.py      # CRUD local groups
│   │   ├── opnsense_auth_priv.py       # Privilege assignment
│   │   ├── opnsense_auth_api_key.py    # API key management
│   │   ├── opnsense_fw_alias.py        # CRUD firewall aliases
│   │   ├── opnsense_fw_filter.py       # CRUD firewall filter rules
│   │   ├── opnsense_fw_dnat.py         # CRUD D-NAT (port forward) rules
│   │   └── opnsense_fw_source_nat.py   # CRUD source NAT rules
│   ├── module_utils/
│   │   └── opnsense_helper.py          # Shared try/except/finally + error mapping
│   ├── filter/                         # Future Jinja2 filters
│   └── inventory/                      # Future inventory plugins
├── roles/
│   ├── auth/
│   │   ├── tasks/main.yml              # Groups → Users → Privileges (ordered)
│   │   ├── defaults/main.yml           # Role variables (no hardcoded values)
│   │   ├── vars/main.yml               # Internal constants
│   │   ├── handlers/main.yml           # Auth is immediate (placeholder)
│   │   └── meta/main.yml               # Galaxy role metadata
│   └── firewall/
│       ├── tasks/main.yml              # Aliases → Filters → D-NAT → SNAT (ordered)
│       ├── defaults/main.yml           # Role variables (no hardcoded values)
│       ├── vars/main.yml               # Internal constants
│       ├── handlers/main.yml           # Firewall apply handler
│       └── meta/main.yml               # Galaxy role metadata
├── inventories/
│   └── opnsense/
│       ├── hosts.yml                   # One host per firewall (connection=local)
│       ├── group_vars/
│       │   └── all.yml                 # Connection defaults (creds via vault)
│       └── host_vars/                  # Per-host overrides
├── playbooks/
│   ├── playbook_auth.yml               # Role-based auth management
│   ├── playbook_auth_e2e.yml           # Auth lifecycle test (32 tasks)
│   └── playbook_fw_e2e.yml             # Firewall lifecycle test (30 tasks)
├── docs/
│   ├── index.md                        # Documentation TOC
│   ├── modules.md                      # Module parameters reference
│   ├── roles.md                        # Role usage + variables
│   ├── inventory.md                    # Inventory + credential setup
│   └── error-handling.md               # Exception → fail_json mapping
└── tests/
    ├── integration/                    # E2E tests against live device
    └── unit/                           # Module unit tests
```

## Modules

### Auth

| Module | Description | Min OPNsense |
|---|---|---|
| `opnsense_auth_user` | CRUD local users (email, password, group membership) | 25.1 |
| `opnsense_auth_group` | CRUD local groups | 25.1 |
| `opnsense_auth_priv` | Assign/unassign privileges to users or groups | 25.1 |
| `opnsense_auth_api_key` | Create/delete API keys for users | 26.1 |

### Firewall

| Module | Description | Min OPNsense |
|---|---|---|
| `opnsense_fw_alias` | CRUD firewall aliases (host, network, port, URL) | 25.1 |
| `opnsense_fw_filter` | CRUD firewall filter rules (pass/block/reject) | 25.1 |
| `opnsense_fw_dnat` | CRUD D-NAT / port forward rules | 26.1 |
| `opnsense_fw_source_nat` | CRUD source NAT / masquerade rules | 25.1 |

All modules support `check_mode` and return `changed`, `action`, `uuid`, and `diff`.

## Roles

| Role | Description |
|---|---|
| `auth` | Manage users, groups, and privileges in correct order |
| `firewall` | Manage aliases, filter rules, D-NAT, and source NAT in correct order |

## Quick Start

### Using the role (recommended)

```yaml
- hosts: all
  connection: local
  vars:
    opn_host: "10.6.224.106"
    opn_key: "{{ vault_opn_key }}"
    opn_secret: "{{ vault_opn_secret }}"
    opn_port: 443
    opn_verify_ssl: false

    opn_groups:
      - name: grp-automation
        description: "Automation accounts"

    opn_users:
      - name: svc-ansible
        email: ansible@example.com

    opn_privileges:
      - priv_id: page-all
        target_type: group
        target_name: grp-automation

  roles:
    - auth
```

### Using modules directly

```yaml
- name: Ensure user exists
  by_systems.opnsense.opnsense_auth_user:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: svc-automation
    email: automation@example.com
    state: present

- name: Create firewall alias
  by_systems.opnsense.opnsense_fw_alias:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    name: svc_web_servers
    type: host
    content: "10.1.3.10\n10.1.3.11"
    description: "Web servers in SVC zone"
    state: present

- name: Allow HTTPS to web servers
  by_systems.opnsense.opnsense_fw_filter:
    host: "{{ opn_host }}"
    key: "{{ opn_key }}"
    secret: "{{ opn_secret }}"
    description: "Allow HTTPS to SVC web servers"
    action: pass
    interface: wan
    direction: in
    protocol: TCP
    destination_net: svc_web_servers
    destination_port: "443"
    state: present
```

### Dry run

```bash
ansible-playbook playbooks/playbook_auth.yml --check
```

### Verbose with logging

```bash
ansible-playbook playbooks/playbook_auth_e2e.yml -vv \
  -e opn_host=10.6.224.106 \
  -e opn_key=<key> \
  -e opn_secret=<secret>

# Logs written to: ~/.opnsense/logs/ansible-opnsense.log (Loki JSON)
```

## Error Handling

All modules use `try/except/finally` (ADR-0029):
- Typed exceptions mapped to `fail_json()` with clear messages
- `finally` block guarantees `client.close()` — no connection leaks
- Log file: `~/.opnsense/logs/ansible-opnsense.log` (structured JSON for Loki)

| Error | Ansible Output |
|---|---|
| Invalid credentials | `"Authentication failed... Check API key and secret."` |
| Validation error | `"Validation failed..."` + field-level details |
| Timeout | `"Request timed out..."` |
| Wrong OPNsense version | `"Endpoint not found... Check OPNsense version >= 26.1."` |

## Credential Options

| Method | Best for |
|---|---|
| Ansible Vault | Production — encrypted at rest |
| Extra-vars (`-e`) | Ad-hoc runs, CI/CD |
| Environment variables | Scripts, containers |

See [docs/inventory.md](docs/inventory.md) for details.

## Development

```bash
git clone https://github.com/by-openclaw/ansible-opnsense.git
cd ansible-opnsense

# Install lib-opnsense from source
pip install -e ../lib-opnsense

# Symlink collection for local development
mkdir -p ~/.ansible/collections/ansible_collections/by_systems
ln -s $(pwd) ~/.ansible/collections/ansible_collections/by_systems/opnsense

# Lint
pip install ansible-lint
ansible-lint plugins/

# Run auth E2E test (requires live OPNsense >= 26.1)
ansible-playbook playbooks/playbook_auth_e2e.yml -vv \
  -e opn_host=<host> -e opn_key=<key> -e opn_secret=<secret>

# Run firewall E2E test
ansible-playbook playbooks/playbook_fw_e2e.yml -vv \
  -e opn_host=<host> -e opn_key=<key> -e opn_secret=<secret> \
  -e opn_port=443 -e opn_verify_ssl=false
```

## Cross-references

| Resource | Location |
|---|---|
| lib-opnsense (Python library) | [by-openclaw/lib-opnsense](https://github.com/by-openclaw/lib-opnsense) |
| API Schema Audit | `platform-setup/tools/opnsense/docs/api-schema-audit.md` |
| API Version Compatibility | `platform-setup/tools/opnsense/docs/api-version-compatibility.md` |
| ADR-0029 (Python lib standard) | `doc-platform-core/docs/adr/0029-python-library-design-standard.md` |
| ADR-0030 (Naming convention) | `doc-platform-core/docs/adr/0030-automation-naming-convention.md` |

## License

MIT
