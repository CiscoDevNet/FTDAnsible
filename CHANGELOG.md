# Changelog
All notable changes to this project will be documented in this file.

## [v0.1.1] - 2019-01-16
### Changed
- Update Ansible module (`ftd_configuration`) to support `upsert` operations for non-creatable objects (e.g., PhysicalInterfaces).

## [v0.1.0] - 2018-11-01
### Added
- Ansible HTTP API plugin that connects to FTD devices over REST API and communicates with them.
- Ansible module (`ftd_configuration`) for managing configuration on FTD devices.
- Ansible module (`ftd_file_download`) for downloading files from FTD devices.
- Ansible module (`ftd_file_upload`) for uploading filed to FTD devices.
