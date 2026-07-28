# Changelog

All notable changes to this project will be documented here.
Format: [Semantic Versioning](https://semver.org)

## [Unreleased]
### Added
- `runner.py` for standardized, easy running of the linting, formatting, and tests.
- New `ValidatorErrorCode`s:
   - `INCOMPATIBLE_LABWARE`
   - `HOLDER_OCCUPIED`
- New `ResolverCode`s:
   - `DESCRIPTOR_INCOMPATIBLE_WITH_LID`
   - `LID_ID_REQUIRED`

### Changed
- `commit-hook` now uses `runner.py`
- `migrate.py` files across `tcode_api.schemas` now type their `MIGRATORS` dict values as
  `Migrator` (from `tcode_api.schemas.registry`) instead of `Callable`.

---

## [1.41.0]
## Added
- `tcode_api.cli.robot_serial_number_annotation` plac canned annotation for providing a target
    robot in preparation for supporting single-robot targeting within fleets.
- Integrate robot targeting by serial number into all tcode_api scripts.
- Update demo plate walkthrough to include pipette volume parametrically

---

## [1.40.1]
## Fixed
- Fix `TCodeServicerClient` requests call to tcode servicer `serial_number_lookup` endpoint

---

## [1.40.0]
### Added
- `TCodeServicerClient.serial_number_lookup` method
- `SerialNumberLookupRequest`, `SerialNumberLookupResponse`, `SerialNumberLookupResult` models for serial number lookup API.
    - API intended to fetch serial numbers of entities resolved to ids by tcode service

### Fixed

### Refactored

---
