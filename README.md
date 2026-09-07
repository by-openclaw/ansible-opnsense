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
ansible-galaxy collection install by_systems-opnsense-0.2.0.tar.gz
```

## Collection Structure

```
ansible-opnsense/
├── galaxy.yml                          # Collection metadata (namespace: by_systems)
├── plugins/
│   ├── modules/                        # 54 thin wrapper modules
│   ├── module_utils/
│   │   └── opnsense_helper.py          # Shared try/except/finally + error mapping
│   ├── filter/                         # Future Jinja2 filters
│   └── inventory/                      # Future inventory plugins
├── roles/                              # 11 roles (one per scope)
│   ├── auth/                           # Groups -> Users -> Privileges (ordered)
│   ├── firewall/                       # Aliases -> Filters -> D-NAT -> SNAT (ordered)
│   ├── interfaces/                     # VLANs, VIPs, bridges, tunnels
│   ├── routing/                        # Gateways -> Routes (ordered)
│   ├── dns/                            # Unbound host overrides, forwarding, ACLs
│   ├── dhcp/                           # Kea DHCPv4/v6 subnets + reservations
│   ├── vpn_ipsec/                      # IPsec connections, children, auth, pools
│   ├── vpn_wireguard/                  # WireGuard servers + clients
│   ├── shaper/                         # Traffic shaper pipes, queues, rules
│   ├── trust/                          # PKI CAs + certificates
│   └── services/                       # Captive portal, cron, DDNS, syslog
├── inventories/
│   └── opnsense/
│       ├── hosts.yml                   # One host per firewall (connection=local)
│       ├── group_vars/
│       │   └── all.yml                 # Connection defaults (creds via vault)
│       └── host_vars/                  # Per-host overrides
├── playbooks/                          # 23 test playbooks
│   ├── {scope}/test_crud.yml           # CRUD lifecycle per scope (10 scopes)
│   ├── {scope}/test_errors.yml         # Error handling per scope (10 scopes)
│   ├── vpn/test_ipsec_crud.yml         # IPsec VPN lifecycle
│   ├── vpn/test_wireguard_crud.yml     # WireGuard VPN lifecycle
│   ├── vpn/test_openvpn_crud.yml       # OpenVPN lifecycle
│   └── test_all.yml                    # Run all scopes
├── docs/
│   ├── index.md                        # Documentation TOC
│   ├── modules.md                      # Module parameters reference (54 modules)
│   ├── api-coverage.md                 # Module status per scope
│   ├── roles.md                        # Role usage + variables
│   ├── inventory.md                    # Inventory + credential setup
│   └── error-handling.md               # Exception -> fail_json mapping
└── tests/
    ├── integration/                    # 30 pytest tests (error, validation, duplicate)
    └── unit/                           # Module unit tests
```

## Modules (54)

### Auth (4 modules)

| Module | Description |
|---|---|
| `opnsense_auth_user` | CRUD local users (email, password, group membership) |
| `opnsense_auth_group` | CRUD local groups |
| `opnsense_auth_priv` | Assign/unassign privileges to users or groups |
| `opnsense_auth_api_key` | Create/delete API keys for users |

### Firewall (8 modules)

| Module | Description |
|---|---|
| `opnsense_fw_alias` | CRUD firewall aliases (host, network, port, URL) |
| `opnsense_fw_filter` | CRUD firewall filter rules (pass/block/reject) |
| `opnsense_fw_dnat` | CRUD D-NAT / port forward rules |
| `opnsense_fw_source_nat` | CRUD source NAT / masquerade rules |
| `opnsense_fw_one_to_one` | CRUD 1:1 NAT (binat) rules |
| `opnsense_fw_category` | CRUD firewall rule categories |
| `opnsense_fw_group` | CRUD firewall interface groups |
| `opnsense_fw_npt` | CRUD IPv6 NPTv6 (NAT66) prefix translation rules |

### Interfaces (9 modules)

| Module | Description |
|---|---|
| `opnsense_if_vlan` | CRUD 802.1Q VLAN sub-interfaces |
| `opnsense_if_vip` | CRUD virtual IP addresses (IP alias, CARP, proxy ARP) |
| `opnsense_if_bridge` | CRUD bridge interfaces |
| `opnsense_if_gif` | CRUD GIF tunnel interfaces |
| `opnsense_if_gre` | CRUD GRE tunnel interfaces |
| `opnsense_if_lagg` | CRUD link aggregation (LAGG) interfaces |
| `opnsense_if_loopback` | CRUD loopback interfaces |
| `opnsense_if_neighbor` | CRUD static ARP / NDP neighbor entries |
| `opnsense_if_vxlan` | CRUD VXLAN tunnel interfaces |

### Routing (2 modules)

| Module | Description |
|---|---|
| `opnsense_rt_gateway` | CRUD gateways (name, interface, protocol) |
| `opnsense_rt_route` | CRUD static routes (network, gateway) |

### DNS / Unbound (6 modules)

| Module | Description |
|---|---|
| `opnsense_ub_host_override` | CRUD local DNS host overrides (A/AAAA/MX/TXT) |
| `opnsense_ub_host_alias` | CRUD host aliases (CNAME-like) |
| `opnsense_ub_forward` | CRUD domain-specific DNS forwarding |
| `opnsense_ub_acl` | CRUD DNS access control lists |
| `opnsense_ub_dot` | CRUD DNS-over-TLS upstream servers |
| `opnsense_ub_diagnostics` | Query Unbound resolver diagnostics (read-only) |
| `opnsense_ub_settings` | Manage Unbound general settings (enable the resolver, port, interfaces, DNSSEC, …) |
| `opnsense_ub_service` | Start / stop / reconfigure the Unbound service |

### DHCP / Kea (5 modules)

| Module | Description |
|---|---|
| `opnsense_kea4_subnet` | CRUD Kea DHCPv4 subnets |
| `opnsense_kea4_reservation` | CRUD Kea DHCPv4 static reservations |
| `opnsense_kea4_peer` | CRUD Kea DHCPv4 HA peers |
| `opnsense_kea6_subnet` | CRUD Kea DHCPv6 subnets |
| `opnsense_kea6_reservation` | CRUD Kea DHCPv6 static reservations |

### WireGuard (2 modules)

| Module | Description |
|---|---|
| `opnsense_wg_server` | CRUD WireGuard server (tunnel) instances |
| `opnsense_wg_client` | CRUD WireGuard client (peer) entries |

### IPsec (8 modules)

| Module | Description |
|---|---|
| `opnsense_ipsec_conn` | CRUD IPsec IKE connections |
| `opnsense_ipsec_child` | CRUD IPsec child SAs |
| `opnsense_ipsec_local` | CRUD IPsec local authentication |
| `opnsense_ipsec_remote` | CRUD IPsec remote authentication |
| `opnsense_ipsec_psk` | CRUD IPsec pre-shared keys |
| `opnsense_ipsec_keypair` | CRUD IPsec key pairs |
| `opnsense_ipsec_pool` | CRUD IPsec address pools |
| `opnsense_ipsec_vti` | CRUD IPsec virtual tunnel interfaces |

### OpenVPN (1 module)

| Module | Description |
|---|---|
| `opnsense_ovpn_instance` | CRUD OpenVPN server or client instances |

### Shaper (3 modules)

| Module | Description |
|---|---|
| `opnsense_ts_pipe` | CRUD traffic shaper bandwidth pipes |
| `opnsense_ts_queue` | CRUD traffic shaper queues |
| `opnsense_ts_rule` | CRUD traffic shaper rules |

### Trust / PKI (2 modules)

| Module | Description |
|---|---|
| `opnsense_trust_ca` | CRUD certificate authorities (internal or imported) |
| `opnsense_trust_cert` | CRUD certificates (internal, external, or imported) |

### Services (4 modules)

| Module | Description |
|---|---|
| `opnsense_cp_zone` | CRUD Captive Portal zones |
| `opnsense_cron_job` | CRUD cron jobs |
| `opnsense_ddns_account` | CRUD dynamic DNS accounts |
| `opnsense_syslog_dest` | CRUD remote syslog destinations |

All modules require OPNsense >= 26.1, support `check_mode`, and return `changed`, `action`, `uuid`, and `diff`.

## Roles (11)

| Role | Description |
|---|---|
| `auth` | Manage users, groups, and privileges in correct order |
| `firewall` | Manage aliases, filter rules, D-NAT, SNAT, 1:1, NPT, categories, groups |
| `interfaces` | Manage VLANs, VIPs, bridges, tunnels, LAGG, loopback, neighbors, VXLAN |
| `routing` | Manage gateways and static routes in correct order |
| `dns` | Manage Unbound host overrides, aliases, forwarding, ACLs, DoT |
| `dhcp` | Manage Kea DHCPv4/v6 subnets, reservations, HA peers |
| `vpn_ipsec` | Manage IPsec connections, children, auth, PSKs, keypairs, pools, VTIs |
| `vpn_wireguard` | Manage WireGuard servers and clients |
| `shaper` | Manage traffic shaper pipes, queues, and rules |
| `trust` | Manage PKI certificate authorities and certificates |
| `services` | Manage captive portal, cron, DDNS, syslog destinations |

## Error Handling (10 exception types)

All modules use `try/except/finally` (ADR-0029). The shared helper in `opnsense_helper.py` catches
all 10 lib-opnsense exception types and maps them to `fail_json()` with clear messages:

| Exception | Ansible Output |
|---|---|
| `AuthenticationError` | `"Authentication failed... Check API key and secret."` |
| `ValidationError` | `"Validation failed..."` + field-level details |
| `TimeoutError` | `"Request timed out..."` |
| `EndpointNotFoundError` | `"Endpoint not found... Check OPNsense version >= 26.1."` |
| `ConnectionError` | `"Connection failed..."` |
| `AmbiguousMatchError` | `"Multiple matches found..."` + match key details |
| `FieldValidationError` | `"Field validation failed..."` + invalid field + allowed values |
| `NotFoundError` | `"Resource not found..."` |
| `ApiError` | `"API error..."` + status code + response |
| `OpnsenseError` | `"Unexpected error..."` (base catch-all) |

Error test playbooks use the `ansible.builtin.assert` pattern with regex to verify exact error messages.

## Static vs Dynamic Enums

Some module parameters use enum choices validated by the OPNsense API, not by Ansible `choices`.
See [lib-opnsense enum-field-reference.md](https://github.com/by-openclaw/lib-opnsense/blob/main/docs/enum-field-reference.md) for the authoritative list.

Key enum fixes in v0.2.0:
- **syslog_dest transport**: `udp4`, `tcp4`, `udp6`, `tcp6`, `tls4`, `tls6`
- **VIP mode**: `ipalias`, `carp`, `proxyarp` (removed `other`)
- **VLAN proto**: `""`, `802.1q`, `802.1ad`

## Verbosity and Logging

| Ansible flag | Log level | What you see |
|---|---|---|
| (none) | WARNING | Errors and warnings only |
| `-v` | INFO | Actions taken (created, updated, deleted, noop) |
| `-vv` | DEBUG | Full API request/response payloads |

Log files are written one per day: `~/.opnsense/logs/ansible-YYYY-MM-DD.log` (structured JSON for Loki).

## Firmware Upgrade Workflow

For firmware upgrades, use the lib-opnsense CLI scripts directly (not Ansible modules):

```bash
# Check available updates
python -m opnsense.scripts.firmware_check --host <host> --key <key> --secret <secret>

# Apply firmware upgrade
python -m opnsense.scripts.firmware_upgrade --host <host> --key <key> --secret <secret>
```

See [lib-opnsense](https://github.com/by-openclaw/lib-opnsense) for details.

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
ansible-playbook playbooks/auth/test_crud.yml -vv \
  -e opn_host=opnsense.example.com \
  -e opn_key=<key> \
  -e opn_secret=<secret>

# Logs written to: ~/.opnsense/logs/ansible-YYYY-MM-DD.log (Loki JSON)
```

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
