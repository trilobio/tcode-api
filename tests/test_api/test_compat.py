"""Unittests for the API migration and compatibility logic."""

import inspect
import logging
import unittest
from contextlib import contextmanager
from typing import Iterator, Literal, cast

from tcode_api.api.compat import (
    APIHistoryLog,
    CompatContext,
    DeprecatedSchemaError,
    InvalidDataError,
    SchemaVersionMismatchError,
    TargetSchemaNotFoundError,
    load_api_object,
    resolve_api_profile,
)
from tcode_api.schemas.base import BaseSchemaVersionedModel
from tcode_api.schemas.registry import MigrationRegistry, RawData, SchemaRegistry


# Copied from py_organelles.log_tools.context_managers
@contextmanager
def modify_log_level(loggers: logging.Logger | list[logging.Logger], level: int) -> Iterator[None]:
    """Temporarily modify the log level of one or more loggers.

    :param logger: logger(s) to modify
    :param level: new log level
    """
    loggers = [loggers] if isinstance(loggers, logging.Logger) else loggers
    # loggers = normalize_logger_list(logger_list)  # Function not defined outside of py-organelles import
    original_levels = [logger.level for logger in loggers]

    try:
        for logger in loggers:
            logger.setLevel(level)
        yield

    finally:
        for logger, original_level in zip(loggers, original_levels):
            logger.setLevel(original_level)


class TestResolveAPIProfile(unittest.TestCase):
    """Tests for the ``resolve_api_profile`` function."""

    def _assert_dicts_equal(self, dict1: dict, dict2: dict) -> None:
        """Helper method to assert that two dicts are equal, ignoring order."""
        missing_keys = set(dict1.keys()) - set(dict2.keys())
        extra_keys = set(dict2.keys()) - set(dict1.keys())
        bad_values = {
            key: (dict1[key], dict2[key])
            for key in dict1
            if key in dict2 and dict1[key] != dict2[key]
        }
        if len(missing_keys) > 0 or len(extra_keys) > 0 or len(bad_values) > 0:
            error_message = (
                "Dicts are not equal:\n" "  Dict1: {dict1}\n" "  Dict2: {dict2}\n"
            ).format(dict1=dict1, dict2=dict2)
            if len(missing_keys) > 0:
                error_message += f"  dict2 missing keys: {missing_keys}\n"
            if len(extra_keys) > 0:
                error_message += f"  dict2 has extra keys: {extra_keys}\n"
            if len(bad_values) > 0:
                for key, (value1, value2) in bad_values.items():
                    error_message += (
                        f"  Key '{key}' has different values: dict1={value1}, dict2={value2}\n"
                    )
            self.fail(error_message)

    def test_replacement_without_increments(self) -> None:
        """Test that a version that had a replacement without any increments still resolves correctly."""
        context = CompatContext(
            migration_registry=MigrationRegistry(),
            schema_registry=SchemaRegistry(),
            api_history_log=APIHistoryLog(
                name="",
                increments={
                    "v0.1.0": {"A": 1, "B": 1, "C": 1},
                    "v0.2.0": {"A": 2, "C": 2},
                },
                migrations={
                    "v0.1.1": {"B": "A"},
                },
            ),
        )

        self._assert_dicts_equal({"A": 2, "C": 2}, resolve_api_profile("v0.2.0", context))

    def test_rename_without_increment(self) -> None:
        """A version with a rename and no increment should resolve correctly."""
        context = CompatContext(
            migration_registry=MigrationRegistry(),
            schema_registry=SchemaRegistry(),
            api_history_log=APIHistoryLog(
                name="test_rename_without_increment",
                increments={
                    "v0.1.0": {"A": 1, "B": 1, "C": 1},
                    "v0.2.0": {"A": 2, "C": 2},
                },
                migrations={
                    "v0.1.1": {"B": "D"},
                },
            ),
        )

        self._assert_dicts_equal({"A": 2, "C": 2, "D": 1}, resolve_api_profile("v0.2.0", context))

    def test_increment_after_rename(self) -> None:
        """A schema renamed in a prior version should increment from the pre-renamed version."""
        context = CompatContext(
            migration_registry=MigrationRegistry(),
            schema_registry=SchemaRegistry(),
            api_history_log=APIHistoryLog(
                name="test_increment_after_rename",
                increments={
                    "v0.1.0": {"A": 1, "B": 1, "C": 1},
                    "v0.2.0": {"A": 2, "C": 2},
                    "v0.3.0": {"D": 2},
                },
                migrations={
                    "v0.2.0": {"B": "D"},
                },
            ),
        )

        self._assert_dicts_equal({"A": 2, "C": 2, "D": 2}, resolve_api_profile("v0.3.0", context))

    def test_increment_and_rename(self) -> None:
        """A schema that is incremented and renamed in a single version should show the increment with the new name."""
        context = CompatContext(
            migration_registry=MigrationRegistry(),
            schema_registry=SchemaRegistry(),
            api_history_log=APIHistoryLog(
                name="test_increment_after_rename",
                increments={
                    "v0.1.0": {"A": 1, "B": 1, "C": 1},
                    "v0.2.0": {"A": 2, "B": 2, "C": 2},
                },
                migrations={
                    "v0.2.0": {"B": "D"},
                },
            ),
        )

        self._assert_dicts_equal({"A": 2, "D": 2, "C": 2}, resolve_api_profile("v0.2.0", context))

    def test_rename_nonexistent(self) -> None:
        """A rename with a non-existent target raises an error."""
        context = CompatContext(
            migration_registry=MigrationRegistry(),
            schema_registry=SchemaRegistry(),
            api_history_log=APIHistoryLog(
                name="test_increment_after_rename",
                increments={
                    "v0.1.0": {"A": 1, "B": 1, "C": 1},
                    "v0.2.0": {"A": 2, "B": 2, "C": 2},
                },
                migrations={
                    "v0.2.0": {"D": "E"},
                },
            ),
        )

        with self.assertRaises(TargetSchemaNotFoundError):
            resolve_api_profile("v0.2.0", context)

    def test_too_early_version(self) -> None:
        """Requesting a version before the first increment should return an empty profile."""
        context = CompatContext(
            migration_registry=MigrationRegistry(),
            schema_registry=SchemaRegistry(),
            api_history_log=APIHistoryLog(
                name="test_too_early_version",
                increments={
                    "v0.1.0": {"A": 1, "B": 1, "C": 1},
                },
            ),
        )
        self._assert_dicts_equal(
            {},
            resolve_api_profile("v0.0.1", context),
        )

    def test_implied_version(self) -> None:
        """Requesting a version that doesn't exist should resolve to the latest version before it."""
        context = CompatContext(
            migration_registry=MigrationRegistry(),
            schema_registry=SchemaRegistry(),
            api_history_log=APIHistoryLog(
                name="test_nonexistent_version",
                increments={
                    "v0.1.0": {"A": 1, "B": 1, "C": 1},
                    "v0.2.0": {"A": 2, "C": 2},
                },
            ),
        )
        self._assert_dicts_equal(
            {"A": 1, "B": 1, "C": 1},
            resolve_api_profile("v0.1.5", context),
        )
        self._assert_dicts_equal(
            {"A": 2, "B": 1, "C": 2},
            resolve_api_profile("v0.2.5", context),
        )

    def test_invalid_version(self) -> None:
        """Test that an error is raised when an invalid version string is specified."""
        bad_versions = ["invalid_version", "version_0.1.0"]
        for bad_version in bad_versions:
            with self.subTest(bad_version=bad_version), self.assertRaises(ValueError):
                resolve_api_profile(
                    bad_version,
                    CompatContext(
                        migration_registry=MigrationRegistry(),
                        schema_registry=SchemaRegistry(),
                        api_history_log=APIHistoryLog(name="test_invalid_version"),
                    ),
                )

    def test_deprecated_version(self) -> None:
        """Test that a version that is deprecated does not show in the final profile."""
        context = CompatContext(
            migration_registry=MigrationRegistry(),
            schema_registry=SchemaRegistry(),
            api_history_log=APIHistoryLog(
                name="test_deprecated_version",
                increments={
                    "v0.1.0": {"A": 1, "B": 1, "C": 1},
                },
                migrations={
                    "v0.2.0": {"A": None},
                },
            ),
        )
        resolve_api_profile("v0.2.0", context)
        self._assert_dicts_equal(
            {"B": 1, "C": 1},
            resolve_api_profile("v0.2.0", context),
        )


class TeacupV1(BaseSchemaVersionedModel):
    """A test schema for testing the load_api_object function."""

    type: Literal["Teacup"] = "Teacup"
    schema_version: Literal[1] = 1


class TeacupV2(BaseSchemaVersionedModel):
    """A test schema for testing the load_api_object function."""

    type: Literal["Teacup"] = "Teacup"
    schema_version: Literal[2] = 2
    was_migrated: bool = False


class CupV1(BaseSchemaVersionedModel):
    """A test schema for testing the load_api_object function."""

    type: Literal["Cup"] = "Cup"
    schema_version: Literal[3] = 3
    was_migrated: bool = False


def migrate_teacup_v1_to_teacup_v2(data: RawData) -> RawData:
    """A simple migration function to migrate from TeacupV1 to TeacupV2."""
    return {
        "type": "Teacup",
        "schema_version": 2,
        "was_migrated": True,
    }


def migrate_teacup_v2_to_cup_v1(data: RawData) -> RawData:
    """A simple migration function to migrate from TeacupV2 to CupV1."""
    return {
        "type": "Cup",
        "schema_version": 3,
        "was_migrated": data.get("was_migrated", False),
    }


class TestLoadAPIObject(unittest.TestCase):
    """Tests for the ``load_api_object`` function."""

    def test_mismatched_schema_versions(self) -> None:
        """Test that an error is raised when the schema version targeted but the api_version doesn't
        match the schema_version in the data packet.
        """
        context = CompatContext(
            migration_registry=MigrationRegistry(),
            schema_registry=SchemaRegistry(
                {
                    "Teacup": TeacupV1,
                },
            ),
            api_history_log=APIHistoryLog(
                name="test_mismatched_schema_versions",
                increments={
                    "v0.1.0": {"Teacup": 1},
                    "v0.2.0": {"Teacup": 2},
                },
            ),
        )
        with (
            self.subTest(msg="schema_version is behind"),
            self.assertRaises(SchemaVersionMismatchError),
        ):
            load_api_object(
                data={"type": "Teacup", "schema_version": 1},
                api_version="v0.2.0",
                context=context,
            )

        with (
            self.subTest(msg="schema_version is ahead"),
            self.assertRaises(SchemaVersionMismatchError),
        ):
            load_api_object(
                data={"type": "Teacup", "schema_version": 2},
                api_version="v0.1.0",
                context=context,
            )

    def test_bad_schema_type(self) -> None:
        """Test that an error is raised when the data packet references a 'type' that isn't
        supported in the target API version.
        """
        context = CompatContext(
            migration_registry=MigrationRegistry(),
            schema_registry=SchemaRegistry(
                {
                    "Teacup": TeacupV1,
                },
            ),
            api_history_log=APIHistoryLog(
                name="test_bad_schema_type",
                increments={
                    "v0.1.0": {"Teacup": 1},
                },
            ),
        )
        with self.assertRaises(TargetSchemaNotFoundError):
            load_api_object(
                data={"type": "Saucer", "schema_version": "v0.1.0"},
                api_version="v0.2.0",
                context=context,
            )

    def test_missing_schema_type(self) -> None:
        """Test that an error is raised when the data packet doesn't include a 'type' field."""
        context = CompatContext(
            migration_registry=MigrationRegistry(),
            schema_registry=SchemaRegistry(
                {
                    "Teacup": TeacupV1,
                },
            ),
            api_history_log=APIHistoryLog(
                name="test_missing_schema_type",
                increments={
                    "v0.1.0": {"Teacup": 1},
                },
            ),
        )
        with self.assertRaises(InvalidDataError):
            load_api_object(
                data={"schema_version": "v0.1.0"},
                api_version="v0.2.0",
                context=context,
            )

    def test_determine_schema_version_from_api_version(self) -> None:
        """Test that if the data packet doesn't include a 'schema_version' field, the function
        determines the correct schema version based on the API version and the API history log.
        """
        context = CompatContext(
            migration_registry=MigrationRegistry(
                _migrators_to_preload={"Teacup": {2: migrate_teacup_v1_to_teacup_v2}},
            ),
            schema_registry=SchemaRegistry(
                _builders_to_preload={
                    "Teacup": TeacupV2,
                },
            ),
            api_history_log=APIHistoryLog(
                name="test_determine_schema_version_from_api_version",
                increments={
                    "v0.1.0": {"Teacup": 1},
                    "v0.2.0": {"Teacup": 2},
                },
            ),
        )
        # This call should succeed and migrate the data from TeacupV1 to TeacupV2, even though the input data
        # doesn't specify a schema_version, because the api_version implies A is V1.
        with (
            modify_log_level(logging.getLogger("tcode_api.api.compat"), logging.ERROR),
            self.subTest(msg="migrate from TeacupV1 to TeacupV2 based on API version"),
        ):
            inst = load_api_object(
                data={"type": "Teacup"},
                api_version="v0.1.0",
                context=context,
            )
            self.assertIsInstance(inst, TeacupV2)
            self.assertEqual(inst.was_migrated, True)  # type: ignore [attr-defined]

        # This call should succeed and create the data as TeacupV2, even though the input data
        # doesn't specify a schema_version, because the api_version implies A is V2.
        with (
            modify_log_level(logging.getLogger("tcode_api.api.compat"), logging.ERROR),
            self.subTest(msg="Load TeacupV2 based on API version"),
        ):
            inst = load_api_object(
                data={"type": "Teacup"},
                api_version="v0.2.0",
                context=context,
            )
            self.assertIsInstance(inst, TeacupV2)
            cast(TeacupV2, inst)
            self.assertEqual(inst.was_migrated, False)  # type: ignore [attr-defined]

    def test_load_schema_versioned_data(self) -> None:
        """Test that data packets with a 'schema_version' field are loaded correctly."""
        context = CompatContext(
            migration_registry=MigrationRegistry(
                _migrators_to_preload={"Teacup": {2: migrate_teacup_v1_to_teacup_v2}},
            ),
            schema_registry=SchemaRegistry(
                _builders_to_preload={
                    "Teacup": TeacupV2,
                },
            ),
            api_history_log=APIHistoryLog(
                name="test_load_schema_versioned_data",
                increments={
                    "v0.1.0": {"Teacup": 1},
                    "v0.2.0": {"Teacup": 2},
                },
            ),
        )
        # This call should succeed and load the data as TeacupV1
        for api_version in ["v0.1.0", "v0.1.5"]:
            with self.subTest(
                msg="Load TeacupV1 based on schema_version in data", api_version=api_version
            ):
                inst = load_api_object(
                    data={"type": "Teacup", "schema_version": 1},
                    api_version=api_version,
                    context=context,
                )
                self.assertIsInstance(inst, TeacupV2)
                self.assertEqual(inst.was_migrated, True)  # type: ignore [attr-defined]

    def test_migrate_through_a_rename(self) -> None:
        """Test that a data packet with an old name is migrated correctly."""
        context = CompatContext(
            migration_registry=MigrationRegistry(
                _migrators_to_preload={
                    "Teacup": {2: migrate_teacup_v1_to_teacup_v2},
                    "Cup": {3: migrate_teacup_v2_to_cup_v1},
                },
            ),
            schema_registry=SchemaRegistry(
                _builders_to_preload={
                    "Teacup": TeacupV2,
                    "Cup": CupV1,
                },
            ),
            api_history_log=APIHistoryLog(
                name="test_migrate_through_a_rename",
                increments={
                    "v0.1.0": {"Teacup": 1},
                    "v0.2.0": {"Teacup": 2},
                    "v0.3.0": {"Cup": 2},
                },
                migrations={
                    "v0.3.0": {"Teacup": "Cup"},
                },
            ),
        )
        with self.subTest(_from="TeacupV1", _to="CupV1"):
            inst = load_api_object(
                data={"type": "Teacup", "schema_version": 1},
                context=context,
            )
            self.assertIsInstance(inst, CupV1)
            self.assertTrue(inst.was_migrated)  # type: ignore [attr-defined]

        with self.subTest(_from="TeacupV2", _to="CupV1"):
            inst = load_api_object(
                data={"type": "Teacup", "schema_version": 2},
                context=context,
            )
            self.assertIsInstance(inst, CupV1)
            self.assertFalse(inst.was_migrated)  # type: ignore [attr-defined]

        with self.subTest(_from="CupV1", _to="CupV1"):
            inst = load_api_object(
                data={"type": "Cup", "schema_version": 3},
                context=context,
            )
            self.assertIsInstance(inst, CupV1)
            self.assertFalse(inst.was_migrated)  # type: ignore [attr-defined]

        # No such thing as a Cup class with schema_version 1
        with self.assertRaises(InvalidDataError):
            load_api_object(
                data={"type": "Cup", "schema_version": 1},
                context=context,
            )

    def test_migrate_through_a_replacement(self) -> None:
        """Test that a data packet whose schema is replaced by another is migrated correctly."""

        class VesselV1(BaseSchemaVersionedModel):
            type: Literal["Vessel"] = "Vessel"
            schema_version: Literal[1] = 1
            volume: float
            was_migrated: bool = False

        def migrate_teacup_v2_to_vessel_v1(data: RawData) -> RawData:
            if data.get("type") != "Teacup" or data.get("schema_version") != 2:
                raise InvalidDataError(
                    data=data,
                    msg="Input data must be of type 'Teacup' with schema_version 2 to migrate to VesselV1",
                )
            return {
                "type": "Vessel",
                "volume": 250.0,
                "schema_version": 1,
                "was_migrated": True,
            }

        context = CompatContext(
            migration_registry=MigrationRegistry(
                _migrators_to_preload={
                    "Teacup": {2: migrate_teacup_v1_to_teacup_v2},
                    "Vessel": {1: migrate_teacup_v2_to_vessel_v1},
                },
            ),
            schema_registry=SchemaRegistry(
                _builders_to_preload={
                    "Teacup": TeacupV2,
                    "Vessel": VesselV1,
                },
            ),
            api_history_log=APIHistoryLog(
                name="test_migrate_through_a_replacement",
                increments={
                    "v0.1.0": {"Teacup": 1},
                    "v0.2.0": {"Teacup": 2, "Vessel": 1},
                },
                migrations={
                    "v0.3.0": {"Teacup": "Vessel"},
                },
            ),
        )
        with self.subTest(_from="TeacupV1", _to="VesselV1"):
            inst = load_api_object(
                data={"type": "Teacup", "schema_version": 1},
                context=context,
            )
            self.assertIsInstance(inst, VesselV1)
            self.assertTrue(inst.was_migrated)  # type: ignore [attr-defined]

    def test_migrate_to_a_deprecation(self) -> None:
        """Test that a data packet whose schema is deprecated raises an error when loaded."""
        context = CompatContext(
            migration_registry=MigrationRegistry(),
            schema_registry=SchemaRegistry(
                _builders_to_preload={
                    "Teacup": TeacupV1,
                },
            ),
            api_history_log=APIHistoryLog(
                name="test_migrate_to_a_deprecation",
                increments={
                    "v0.1.0": {"Teacup": 1},
                },
                migrations={
                    "v0.2.0": {"Teacup": None},
                },
            ),
        )

        for api_version in [None, "v0.2.0"]:
            with (
                self.subTest(api_version=api_version),
                self.assertRaises((TargetSchemaNotFoundError, DeprecatedSchemaError)),
            ):
                load_api_object(
                    data={"type": "Teacup", "schema_version": 1},
                    context=context,
                    api_version=api_version,
                )


class TestTCodeAPI(unittest.TestCase):
    """Test that all entities in the tcode_api.api package are correctly represented in the API history log."""

    def _get_most_recent_api_profile(self, compat_context: CompatContext) -> dict[str, int]:
        """Helper method to get the most recent API profile from the compat context."""
        api_version_str = compat_context.api_history_log.get_most_recent_version()
        return resolve_api_profile(api_version_str, compat_context)

    def _validate_compat_context(self, compat_context: CompatContext) -> None:
        """Validate that the compat structure is well-formed, e.g. that all of the internal
        structures match up.

        Current checks:
          * All builders in the schema_registry are represented in the API history log.
          * All of the most modern entries in the api_history_log are registered with the schema_registry.
        """
        profile = self._get_most_recent_api_profile(compat_context)
        schemas_without_builders: list[str] = [
            name for name in profile if name not in compat_context.schema_registry.keys
        ]
        if len(schemas_without_builders) > 0:
            self.fail(
                f"The following schemas are in the API history log but don't have builders registered in the schema registry: {schemas_without_builders}"
            )
        builders_without_schemas: list[str] = [
            name for name in compat_context.schema_registry.keys if name not in profile
        ]
        if len(builders_without_schemas) > 0:
            self.fail(
                f"The following schemas have builders registered in the schema registry but aren't in the API history log: {builders_without_schemas}"
            )

    def test_tcode_api_matches_compat_context(self) -> None:
        """Test that all entities in the tcode_api.api package are correctly represented in the API history log."""
        import tcode_api.api as tc
        from tcode_api.api.compat import tcode_api_compat_context

        # Some exposed entities in tcode_api are unversioned and are expected to not be in the API profile.
        # We exclude those here.
        api_versioned_entity_names = [
            t[0]
            for t in inspect.getmembers(tc, inspect.isclass)
            if issubclass(t[1], BaseSchemaVersionedModel)
        ]

        profile = self._get_most_recent_api_profile(tcode_api_compat_context)
        missing_from_profile = [name for name in api_versioned_entity_names if name not in profile]
        if len(missing_from_profile) > 0:
            self.fail(
                f"The following entities are `schema_version`ed entities exposed in tcode_api.api but not represented in the API history log for the most recent version: {missing_from_profile}"
            )


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    unittest.main()
