# Changelog

All notable changes to this project will be documented here.
Format: [Semantic Versioning](https://semver.org)

## [v1.43.0]
## Added
- Expose lower-level `is_description_or_descriptor` to allow external code that doesn't need the
    schema to check if a dict is a description or descriptor.
- Expose lower-level `migrate_data_to_version` to target specific versions and make unittests more
    portable (they don't break when registering to the latest version automatically).
- `tcode_api.api.LiddabilityDescript[ion|or]` schemas to marshal all data regarding the
    liddability of a labware: can it be lidded, where does the lid go, and what kind of lid is it.
- `supports_lid` argument to `describe_well_plate` that allows the easy creation of an unlidded
    lid-supporting labware while maintaining backward-compatible scripts.

## Changed
- `tcode_api.api.WellPlateDescript[ion|or]` schemas migrated to v5 to include `Liddability` schema.


## [1.42.1]
## Added
- Added party mode script
- Default progress display for `TCodeServicerClient.run_script()`

## Fixed
- Fixed mismatching batch scheduling type between TCode server and client

---

## [v1.42.0]
### Added
- pull request template, modeled after that of `aceta`
- `runner.py` for standardized, easy running of the linting, formatting, and tests.
- New `ValidatorErrorCode`s:
   - `INCOMPATIBLE_LABWARE`
   - `HOLDER_OCCUPIED`
- New `ResolverCode`s:
   - `DESCRIPTOR_INCOMPATIBLE_WITH_LID`
   - `LID_ID_REQUIRED`
- `pinchable` field on `Lid`, `WellPlate`, `Trash`, `TubeHolder`, and `PipetteTipBox`
  descriptions/descriptors (v4), indicating whether the labware can be lifted with a pinch grip.
  Introduced via new `base/labware_description/v2.py` (`BaseLabwareDescriptionV2`/
  `BaseLabwareDescriptorV2`) so v1-v3 schemas are untouched; v3->v4 migration backfills
  `pinchable` per labware kind (`True` for Lid/WellPlate, `False` for
  Trash/TubeHolder/PipetteTipBox), matching existing pinch-vs-lift behavior in `robot`/`tcode`.
- `pinch_offset_transform` field on `BaseLabwareDescriptionV2`/`BaseLabwareDescriptorV2`, required
  when `pinchable` is `True` (validated) and disallowed otherwise. `Lid`/`WellPlate`'s v3->v4
  migration backfills it from the historical pinch offsets in `tcode.resolver.create_labware`
  (2mm/10mm in z respectively).
- `scripts/migrate_schemas.py` tool to migrate tcode_labware automatically.
- run_tests workflow

### Changed
- `commit-hook` now uses `runner.py`
- `migrate.py` files across `tcode_api.schemas` now type their `MIGRATORS` dict values as
  `Migrator` (from `tcode_api.schemas.registry`) instead of `Callable`.
- Shared base classes (`BaseTCodeCommand`, `BaseLabwareDescription`, etc.) moved from flat
  `base.py` files into versioned `base/<model>/v1.py` packages, one model per file
  (`Description`/`Descriptor` pairs kept together), with class names suffixed `V1`. No
  behavior change; internal-only, not part of the public API.
- Added `DiscoverFleetRequest` and `DiscoverFleetResponse` models for fleet discovery API.
- `LabwareIO` replaced with `SchemaIO` in `tcode_api.utilities`: dispatches by each file's own
  `"type"` field via `schema_registry` instead of a hardcoded `LabwareDescription` adapter, so
  one instance can load a directory mixing schema kinds, and `load()` now migrates data to the
  current version before validating instead of failing on stale fixtures. `load_labware()` keeps
  its prior signature/return type as a thin wrapper. `scripts/migrate_labware.py` renamed to
  `scripts/migrate_schemas.py` and simplified accordingly.

### Fixed
- standardize usage of `Field(examples=...)` in `servicer_api` to avoid `pydantic` warnings about `example=...` being deprecated
- All `Description`/`Descriptor` builders (`_build_lid`, `_build_well_plate`, `_build_grid`,
  etc. -- 15 total) fell back from the strict `Description` to the all-optional `Descriptor`
  on *any* `ValidationError`, silently masking real validation failures (e.g. a `pinchable=True`
  labware missing its required `pinch_offset_transform`) as if the data were merely a partial
  record. New shared `schemas.registry.build_description_or_descriptor` helper narrows the
  fallback to `ValidationError`s where every reported error is a missing field.

### Deprecated
- Dropped support for python 3.11

---

## [1.41.0]
## Added
- `tcode_api.cli.robot_serial_number_annotation` plac canned annotation for providing a target
    robot in preparation for supporting single-robot targeting within fleets.
- Integrate robot targeting by serial number into all tcode_api scripts.
- Update demo plate walkthrough to include pipette volume parametrically

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
