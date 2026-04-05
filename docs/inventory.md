# Inventory & Credentials

## Inventory Structure

```
inventories/opnsense/
  hosts.yml              # One host per firewall
  group_vars/
    all.yml              # Shared connection defaults
  host_vars/
    opnsense-01.yml      # Per-host overrides
```

## hosts.yml

```yaml
all:
  hosts:
    opnsense-01:
      ansible_host: 10.6.224.106
      ansible_connection: local  # API calls run locally
```

## Credentials

**Never commit credentials.** Use one of:

### Option 1: Ansible Vault (recommended)

```bash
# Create vault file
ansible-vault create inventories/opnsense/group_vars/vault.yml

# Contents:
vault_opn_key: "your-api-key"
vault_opn_secret: "your-api-secret"

# Reference in group_vars/all.yml:
opn_key: "{{ vault_opn_key }}"
opn_secret: "{{ vault_opn_secret }}"

# Run:
ansible-playbook -i inventories/opnsense --ask-vault-pass playbooks/playbook_auth.yml
```

### Option 2: Extra-vars

```bash
ansible-playbook playbooks/playbook_auth.yml \
  -e opn_host=10.6.224.106 \
  -e opn_key=<key> \
  -e opn_secret=<secret>
```

### Option 3: Environment variables

```bash
export OPN_HOST=10.6.224.106
export OPN_KEY=<key>
export OPN_SECRET=<secret>

# In playbook vars:
opn_host: "{{ lookup('env', 'OPN_HOST') }}"
opn_key: "{{ lookup('env', 'OPN_KEY') }}"
opn_secret: "{{ lookup('env', 'OPN_SECRET') }}"
```
