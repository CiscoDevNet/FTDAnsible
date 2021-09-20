# Sample compatibility with different FTD versions

As FTD API evolves, it changes between releases and does not always guarantee backward 
compatibility. Thus, some playbook samples might not work with previous versions of FTD.

We aim to keep playbooks up-to-date and make them all work with the latest FTD version. 
To check if a certain playbook is compatible with a previous FTD release, see the compatibility 
table.

## Samples in `ftd_configuration`

| Name | FTD 6.2.3 | FTD 6.3.0 | FTD 6.4.0 | FTD 6.5.0 | FTD 7.0.0 |
| ----------- | :-------: | :-----: | :-----: | :-----: |
| `access_policy.yaml` | ✔ | ✔ | ✔ | ✔ | ? |
| `access_rule_with_applications.yml` | ✔ | ✔ | ✔ | ✔ | ? |
| `access_rule_with_intrusion_and_file_policies.yml` | ✔ | ✔ | ✔ | ✔ | ? |
| `access_rule_with_logging.yml` | ✖ | ✔ | ✔ | ✔ | ? |
| `access_rule_with_networks.yml` | ✖ | ✔ | ✔ | ✔ | ? |
| `access_rule_with_urls.yml` | ✔ | ✔ | ✔ | ✔ | ? |
| `access_rule_with_users.yml` | ✖ | ✖ | ✔ | ✔ | ? |
| `anyconnect_package_file.yml` | ✔ | ✔ | ✔ | ✔ | ? |
| `backup.yml` | ✔ | ✔ | ✔ | ✔ | ? |
| `data_dns_settings.yml` | ✖ | ✔ | ✔ | ✔ | ? |
| `deployment.yml` | ✖ | ✔ | ✔ | ✔ | ? |
| `dhcp_container.yml` | ✖ | ✔ | ✔ | ✔ | ? |
| `download_upload.yml` | ✔ | ✔ | ✔ | ✔ | ? |
| `ha_join.yml` | ✖ | ✔ | ✔ | ✔ | ? |
| `identity_policy.yml` | ✖ | ✖ | ✔ | ✔ | ? |
| `initial_provisioning.yml` | ✖ | ✔ | ✔ | ✔ | ? |
| `nat.yml` | ✔ | ✔ | ✔ | ✔ | ? |
| `network_object.yml` | ✔ | ✔ | ✔ | ✔ | ? |
| `network_object_with_host_vars.yml` | ✔ | ✔ | ✔ | ✔ | ? |
| `physical_interface.yml` | ✖ | ✔ | ✔ | ✔ | ? |
| `port_object.yml` | ✔ | ✔ | ✔ | ✔ | ? |
| `ra_vpn.yml` | ✖ | ✖ | ✔ | ✔ | ? |
| `ra_vpn_license.yaml` | ✔ | ✔ | ✔ | ✔ | ? |
| `security_intelligence_url_policy.yml` | ✖ | ✔ | ✔ | ✔ | ? |
| `smart_license.yml` | ✔ | ✔ | ✔ | ✔ | ? |
| `ssl_policy.yml` | ✔ | ✔ | ✔ | ✔ | ? |
| `static_route_entry.yml` | ✔ | ✔ | ✔ | ✔ | ? |
| `sub_interface.yml` | ✖ | ✔ | ✔ | ✖ | ? |

## Samples in `deployment/vmware`

| Name | FTD 6.2.3 | FTD 6.3.0 | FTD 6.4.0 | FTD 6.5.0 | FTD 7.0.0 |
| ----------- | :-------: | :-----: | :-----: | :-----: | :-----: |
| deploy.yml | ✔ | ✔ | ✔ | ✔ | ✔ |
| destroy.yml | ✔ | ✔ | ✔ | ✔ | ✔ |
| deploy_and_destroy.yml | ✔ | ✔ | ✔ | ✔ |