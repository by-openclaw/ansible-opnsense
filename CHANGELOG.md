# Changelog

## [0.4.0](https://github.com/by-openclaw/ansible-opnsense/compare/v0.3.0...v0.4.0) (2026-09-16)


### Features

* **acme:** opnsense_acme_{settings,account,validation,action,certificate,service} modules ([506d891](https://github.com/by-openclaw/ansible-opnsense/commit/506d8918b35ddc5a6d207173c2602c5d44ed96da))
* **acme:** opnsense_acme_settings cron option (renewal cron via fetchCronIntegration) ([637b814](https://github.com/by-openclaw/ansible-opnsense/commit/637b814f84f78da3c37f75e1d14d5bc56c839ef6))
* **acme:** settings module cron option — the plugin's renewal cron via fetchCronIntegration ([b6ddbca](https://github.com/by-openclaw/ansible-opnsense/commit/b6ddbcaa6590298d99e61fedcb7ced36b822bf56))
* **acme:** six opnsense_acme_* modules over the lib ACME managers (GUI cert via the catalog) ([4d05d5d](https://github.com/by-openclaw/ansible-opnsense/commit/4d05d5d80b8cee09c153069fc6bc1b5b658b475a))
* **crowdsec:** opnsense_crowdsec_settings + opnsense_crowdsec_service modules ([b4ced7c](https://github.com/by-openclaw/ansible-opnsense/commit/b4ced7c91c27cd2a9ab3348bc26f6b32b102d07a))
* **crowdsec:** opnsense_crowdsec_settings + opnsense_crowdsec_service modules ([ca33b74](https://github.com/by-openclaw/ansible-opnsense/commit/ca33b74e3640d95e58a870c88eaae9cefb974355))
* **dhcp:** Kea settings/service, radvd entry/service, dnsmasq settings/service modules; kea4_subnet option_data ([74ba4b7](https://github.com/by-openclaw/ansible-opnsense/commit/74ba4b7a7c59465be74a528d997be5ca4effd4b9))
* **dhcp:** Kea settings/service, radvd entry/service, dnsmasq settings/service modules; kea4_subnet option_data ([84bd199](https://github.com/by-openclaw/ansible-opnsense/commit/84bd1995281dc0d77ba743b08daac17c83b27bcf)), closes [#18](https://github.com/by-openclaw/ansible-opnsense/issues/18)
* **dns:** opnsense_ub_settings + opnsense_ub_service modules (Unbound general block + service) ([399bc67](https://github.com/by-openclaw/ansible-opnsense/commit/399bc678700685de3331a2d691f64e9ead8ab73c))
* **dns:** opnsense_ub_settings + opnsense_ub_service modules (Unbound general block + service) ([cf3b405](https://github.com/by-openclaw/ansible-opnsense/commit/cf3b405aa4a96dabc66e9c0defd6f46f28e3040d))
* **fw_dnat:** source/destination match, sequence, natreflection, nordr ([2246db6](https://github.com/by-openclaw/ansible-opnsense/commit/2246db69123eb4c9279c08c4c3d843d44cad8699))
* **fw_dnat:** source/destination match, sequence, natreflection, nordr ([54697f3](https://github.com/by-openclaw/ansible-opnsense/commit/54697f3300a6623101d8b05f82955a17853a1ed1))
* **fw_filter:** expose quick, sequence, source_not, destination_not, gateway ([0fd3b3d](https://github.com/by-openclaw/ansible-opnsense/commit/0fd3b3d7a77c95ec199e2eeaa104403b69a8af86))
* **fw_filter:** expose quick, sequence, source_not, destination_not, gateway ([20fb4d4](https://github.com/by-openclaw/ansible-opnsense/commit/20fb4d4791eb4c2b5329cf835899ad7d1cfa0ac0))
* **ids:** opnsense_ids_settings detect_profile (nested detect.Profile, lib [#106](https://github.com/by-openclaw/ansible-opnsense/issues/106)) ([56a66ee](https://github.com/by-openclaw/ansible-opnsense/commit/56a66ee2e092dac408d57f7c5b5ae2ebeb42bde0))
* **ids:** opnsense_ids_settings detect_profile (nested detect.Profile) ([ab323b6](https://github.com/by-openclaw/ansible-opnsense/commit/ab323b63044b52a3de90d945360b37d80542da62))
* **ids:** Suricata settings/ruleset/service + mDNS repeater settings/service modules ([ac46857](https://github.com/by-openclaw/ansible-opnsense/commit/ac468579a9cb03faf84e5bc06fa8eb6e04334ed6))
* **ids:** Suricata settings/ruleset/service + mDNS repeater settings/service modules ([9f54008](https://github.com/by-openclaw/ansible-opnsense/commit/9f54008b491a5e0c879422ff5d184477e8ce91ed)), closes [#18](https://github.com/by-openclaw/ansible-opnsense/issues/18)
* **modules:** expose ensure(dedupe) on every resource module ([8e79b84](https://github.com/by-openclaw/ansible-opnsense/commit/8e79b8405d9f1dde2d3db9fc07405677c7378a00))
* **modules:** expose ensure(dedupe) on every resource module ([09a4695](https://github.com/by-openclaw/ansible-opnsense/commit/09a4695ea3051db9d8d233104fdeaf5e8bf6caae))
* **monit:** opnsense_monit_daemon — drive the Monit daemon (lib MonitDaemonManager) ([af5a263](https://github.com/by-openclaw/ansible-opnsense/commit/af5a26390d3492308fd25342ec2276fa1b25e3e4))
* **monit:** opnsense_monit_daemon — start/stop/reconfigure the Monit daemon (lib MonitDaemonManager) ([b356c97](https://github.com/by-openclaw/ansible-opnsense/commit/b356c97104c7ea79f89b68ad367eb4597216275a))
* plugin / firmware / core-service / ddns+netflow service / monit x4 modules; rt_gateway for dynamic gateways ([f0cd4c5](https://github.com/by-openclaw/ansible-opnsense/commit/f0cd4c525825c0be5dde8cc47509edafeacd41de))
* plugin / firmware / core-service / ddns+netflow service / monit x4 modules; rt_gateway for dynamic gateways ([e46a386](https://github.com/by-openclaw/ansible-opnsense/commit/e46a386c33107ee6a2de5eecb969cdb05bd290b9)), closes [#18](https://github.com/by-openclaw/ansible-opnsense/issues/18)
* **provisioning:** opnsense_seed_import — seed a fresh FW through its boot importer, no shell script ([5190138](https://github.com/by-openclaw/ansible-opnsense/commit/5190138eeb4bdd7c42c27f19200b6405ea9e1c48))
* **provisioning:** opnsense_seed_import — seed a fresh FW through its boot importer, no shell script ([993d1c9](https://github.com/by-openclaw/ansible-opnsense/commit/993d1c91f3f8ca1375d93187c4077d628c71ea01))
* **radvd:** expose the RFC 8106 resolver fields on the entry module ([e4131b8](https://github.com/by-openclaw/ansible-opnsense/commit/e4131b8d4e4011e3edd3ba0b4a8d8b4a82ebd192))
* **radvd:** expose the RFC 8106 resolver fields on the entry module ([51191eb](https://github.com/by-openclaw/ansible-opnsense/commit/51191eb8523f3e8386a44f2d49791540b86fc5a8))
* **seed-config:** give an OOB-only firewall its route from the seed ([0c9bacd](https://github.com/by-openclaw/ansible-opnsense/commit/0c9bacd84eaf9664237c3a3980f7630c60cad67f))
* **seed-config:** let a seed name the resolvers a fresh box boots with ([54fdcb7](https://github.com/by-openclaw/ansible-opnsense/commit/54fdcb717fe72cdbb0b39352b6e57ecdcbc971b6))
* **seed-config:** let a seed name the resolvers a fresh box boots with ([c6f495a](https://github.com/by-openclaw/ansible-opnsense/commit/c6f495ad6309df440da317c444b8d85c092a3d11))
* **seed-config:** render a fresh firewall's config.xml from Ansible ([0c334fe](https://github.com/by-openclaw/ansible-opnsense/commit/0c334fe792284eaa6ffbbe408800c17c962a513e))
* **seed-config:** render a fresh firewall's config.xml from Ansible ([bf4efc2](https://github.com/by-openclaw/ansible-opnsense/commit/bf4efc233e9430caa87a4ec325e525b96d50430c))
* **seed-config:** take credentials from Vault, fall back to files ([37f5e3c](https://github.com/by-openclaw/ansible-opnsense/commit/37f5e3c9aef41b6bbe9c5e6c68f9585ead59e93a))
* **seed-config:** take credentials from Vault, fall back to files ([f08fda5](https://github.com/by-openclaw/ansible-opnsense/commit/f08fda564d9327d7edc36a165640510ff8ff8989))
* **seed:** ssh_port + ssh_interfaces are seed-owned (appliance sshd on the hardening port, OOB only) ([73f2cf4](https://github.com/by-openclaw/ansible-opnsense/commit/73f2cf4ace0525a2d9244e30d408eaa55057095f))
* **seed:** ssh_port + ssh_interfaces are seed-owned (appliance sshd on the hardening port, OOB only) ([129b5c0](https://github.com/by-openclaw/ansible-opnsense/commit/129b5c0fbceb36b446c08b8842fedab8121763fc))
* **seed:** webgui_acme_fqdn pre-binds the GUI to the certificate the ACME client will issue ([e499a5f](https://github.com/by-openclaw/ansible-opnsense/commit/e499a5fabc94b1964ccb2fbd1d6185b70b4781e1))
* **seed:** webgui_acme_fqdn pre-binds the GUI to the certificate the ACME client will issue ([5941037](https://github.com/by-openclaw/ansible-opnsense/commit/5941037e5ec82b0aeef4f46ad044ca1e89bdf2a6))
* **seed:** webgui_althostnames + sudo_allow_wheel are seed-owned ([3f38518](https://github.com/by-openclaw/ansible-opnsense/commit/3f38518aa052ade7db3dfbe85b54521bb0e9fb3e))
* **seed:** webgui_althostnames + sudo_allow_wheel are seed-owned ([9342954](https://github.com/by-openclaw/ansible-opnsense/commit/93429543629103f55c0798289b05ee7183dafbf1))
* **services:** chrony / lldpd / qemu-guest-agent / dnscrypt-proxy settings + service modules ([35d48aa](https://github.com/by-openclaw/ansible-opnsense/commit/35d48aa8772710853f5e7f5855f8720d1113f439))
* **services:** chrony / lldpd / qemu-guest-agent / dnscrypt-proxy settings + service modules ([0859fe3](https://github.com/by-openclaw/ansible-opnsense/commit/0859fe326f331b2119590c1741ff30f71b0222c6)), closes [#18](https://github.com/by-openclaw/ansible-opnsense/issues/18)


### Bug Fixes

* **seed-import:** check mode must not fail when the VM does not exist yet ([c756f7d](https://github.com/by-openclaw/ansible-opnsense/commit/c756f7db1bbe411b2d788bb18d721d19b8a3b907))
* **seed-import:** check mode must not fail when the VM does not exist yet ([c498cba](https://github.com/by-openclaw/ansible-opnsense/commit/c498cba7752e96e613232083f0beb11047db1f7b))

## [0.3.0](https://github.com/by-openclaw/ansible-opnsense/compare/v0.2.0...v0.3.0) (2026-06-13)


### Features

* **services:** forward Cloudflare-required fields in opnsense_ddns_account ([166f1cc](https://github.com/by-openclaw/ansible-opnsense/commit/166f1cc1e6cf5987b1aaea89e973a9108d7c6469))
* **services:** forward zone/ttl/force_ssl/wildcard/resourceId/checkip_timeout in opnsense_ddns_account ([4d4f1d6](https://github.com/by-openclaw/ansible-opnsense/commit/4d4f1d698f382d848f71ceb90ea787f57eb2139b)), closes [#8](https://github.com/by-openclaw/ansible-opnsense/issues/8)


### Bug Fixes

* **agents:** link to doc-platform-core for agent contract files ([9d8e425](https://github.com/by-openclaw/ansible-opnsense/commit/9d8e425651dc64a5ea99b10da379dc49c95345f1))
* **agents:** remove unreachable OPERATING-STANDARD.md link ([e67163d](https://github.com/by-openclaw/ansible-opnsense/commit/e67163d406717a97570106e455ed4ca9ebfde983))
* **agents:** restore OPERATING-STANDARD reference as plain text ([706e648](https://github.com/by-openclaw/ansible-opnsense/commit/706e6485fcdbc7d2c340dec933f5b25f90658dc8))

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
