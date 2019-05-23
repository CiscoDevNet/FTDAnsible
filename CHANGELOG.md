# Changelog
All notable changes to this project will be documented in this file.

## [v0.2.1] - 2019-05-23
### Added
- Ansible playbooks for configuring DHCP servers and Static Routes.
### Changed
- `firepower-kickstart` dependency used in `ftd_install` module being installed from official PyPI.

## [v0.2.0] - 2019-04-12
### Added
- Ansible module (`ftd_install`) for installing package images on hardware FTD device.
- Ansible playbooks for provisioning virtual FTDs on AWS, KVM, and VMware platforms.
### Changed
- Dynamic lookup of API version in FTD HTTP API plugin.
- More Ansible playbooks for various FTD configurations (advanced Access Rules, registering Smart License, creating a backup, etc).
- Automatic [removal of duplicates](https://github.com/CiscoDevNet/FTDAnsible/issues/79) from reference lists for better idempotency.

## [v0.1.1] - 2019-01-16
### Changed
- Update Ansible module (`ftd_configuration`) to support `upsert` operations for non-creatable objects (e.g., PhysicalInterfaces).

## [v0.1.0] - 2018-11-01
### Added
- Ansible HTTP API plugin that connects to FTD devices over REST API and communicates with them.
- Ansible module (`ftd_configuration`) for managing configuration on FTD devices.
- Ansible module (`ftd_file_download`) for downloading files from FTD devices.
- Ansible module (`ftd_file_upload`) for uploading filed to FTD devices.
