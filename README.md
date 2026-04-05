# BY-SYSTEMS OPNsense Ansible Collection

Thin Ansible modules wrapping [lib-opnsense](https://github.com/by-openclaw/lib-opnsense) -- the async Python library for the OPNsense REST API.

All API logic, retry handling, and idempotency live in lib-opnsense. These modules are intentionally minimal: they translate Ansible parameters into `ensure()` calls and return structured results.

## Requirements

- Python 3.10+
- Ansible 2.15+
- lib-opnsense (`pip install opnsense` or from source)

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

## Modules

| Module | Description |
|---|---|
| `by_systems.opnsense.opnsense_auth_user` | Manage OPNsense local users (create/update/delete) |
| `by_systems.opnsense.opnsense_auth_group` | Manage OPNsense local groups (create/update/delete) |

All modules support `check_mode` and return `changed`, `action`, `uuid`, and `diff`.

## Usage

### Environment variables

Set OPNsense credentials as environment variables:

```bash
export OPN_HOST=10.6.224.106
export OPN_KEY=your-api-key
export OPN_SECRET=your-api-secret
```

### Playbook example

```yaml
- name: OPNsense auth management
  hosts: localhost
  connection: local
  gather_facts: false
  vars:
    opn_host: "{{ lookup('env', 'OPN_HOST') }}"
    opn_key: "{{ lookup('env', 'OPN_KEY') }}"
    opn_secret: "{{ lookup('env', 'OPN_SECRET') }}"
  tasks:
    - name: Ensure automation group exists
      by_systems.opnsense.opnsense_auth_group:
        host: "{{ opn_host }}"
        key: "{{ opn_key }}"
        secret: "{{ opn_secret }}"
        name: grp-automation
        description: "Automation service accounts"
        state: present

    - name: Ensure service account exists
      by_systems.opnsense.opnsense_auth_user:
        host: "{{ opn_host }}"
        key: "{{ opn_key }}"
        secret: "{{ opn_secret }}"
        name: svc-automation
        email: automation@by-systems.be
        state: present
```

### Dry run

```bash
ansible-playbook playbooks/playbook_auth.yml --check
```

## Development

```bash
git clone https://github.com/by-openclaw/ansible-opnsense.git
cd ansible-opnsense

# Install lib-opnsense from source
pip install git+https://github.com/by-openclaw/lib-opnsense.git

# Lint
pip install ansible-lint
ansible-lint plugins/

# Run integration playbook (requires live OPNsense)
ansible-playbook playbooks/playbook_auth.yml
```

## License

MIT
