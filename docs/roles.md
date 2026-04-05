# Roles

## auth

Manage OPNsense users, groups, and privilege assignments.

### Variables

Define in playbook vars, group_vars, host_vars, or extra-vars:

```yaml
opn_groups:
  - name: grp-automation
    description: "Automation accounts"
    state: present

opn_users:
  - name: svc-ansible
    email: ansible@example.com
    password: "{{ vault_password }}"
    group_memberships: "2000"  # GID, not UUID
    state: present

opn_privileges:
  - priv_id: page-all
    target_type: group
    target_name: grp-automation
    state: present
```

### Execution Order

1. Groups (created first so users can reference them)
2. Users (with optional group membership)
3. Privileges (assigned to existing users/groups)

### Usage

```yaml
- hosts: all
  connection: local
  roles:
    - auth
```

### Notes

- Auth changes on OPNsense are **immediate** — no reconfigure needed
- Group memberships use **GID** (numeric), not UUID (OPNsense 26.1)
- Passwords are `no_log: true` — never shown in output
