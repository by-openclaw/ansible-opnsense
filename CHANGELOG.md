# Changelog

## [0.2.0](https://github.com/by-openclaw/ansible-opnsense/compare/v0.1.0...v0.2.0) (2026-04-12)


### Features

* **auth:** complete collection with roles, inventory, docs, E2E playbook ([#2](https://github.com/by-openclaw/ansible-opnsense/issues/2)) ([3fdbc38](https://github.com/by-openclaw/ansible-opnsense/commit/3fdbc38c1a792b5aaf1a395fc909eadb1b47e594))
* **firewall:** alias, filter, dnat, source_nat modules + role ([#3](https://github.com/by-openclaw/ansible-opnsense/issues/3)) ([a37b03c](https://github.com/by-openclaw/ansible-opnsense/commit/a37b03c8da6a06aaecb5d65d075d74d3691bd915))
* initial scaffold — opnsense_auth_user, opnsense_auth_group modules ([d944730](https://github.com/by-openclaw/ansible-opnsense/commit/d9447306c06b6977880b96d02e1df0516a2cc6a5))


### Bug Fixes

* **ci:** remove ansible.builtin from galaxy.yml dependencies ([3d70286](https://github.com/by-openclaw/ansible-opnsense/commit/3d7028660e3201c4c3cd2459e8d79d2c4b1eb153))
* **ci:** use RUNE_GITHUB_TOKEN for private lib-opnsense git clone ([3e78f53](https://github.com/by-openclaw/ansible-opnsense/commit/3e78f53f567ee2862a968fccb3646f11dbe540d1))
* **collection:** 54 modules, 11 roles, 23 playbooks — full OPNsense API coverage ([c2bc34e](https://github.com/by-openclaw/ansible-opnsense/commit/c2bc34e79c906a6e9ec2fa8e7c9a476a78950d8d))
* **collection:** 54 modules, 11 roles, 23 playbooks — full OPNsense API coverage ([2386fde](https://github.com/by-openclaw/ansible-opnsense/commit/2386fdeb135592da61807aba3183463f7cdc3c02))
* file headers, copyright BY-SYSTEMS SRL, replace real domains with example.com ([5b94d22](https://github.com/by-openclaw/ansible-opnsense/commit/5b94d221f10453cdbe3e66f1429cdfb7b0ca1790))

## [Unreleased]

### Features

* Initial scaffold -- opnsense_auth_user, opnsense_auth_group modules
* Thin wrappers around lib-opnsense Python library
