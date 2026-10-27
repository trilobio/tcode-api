"""Unittests for tcode-api's migration and compatibility logic.

The generic machinery is tested in py-organelles, alongside ``py_organelles.schema_versioning``.
These tests cover tcode-api's own schemas, migrators, and ``tcode_api_compat_context``.
"""

import dataclasses
import inspect
import logging
import unittest
from pathlib import Path

from pydantic import ValidationError

import tcode_api.api as tc  # This import allows us to test what a "customer" who imports TCode would see
from tcode_api.api.compat import (
    CompatContext,
    load_api_object,
    migrate_data_to_latest,
    migrate_data_to_version,
    read_and_migrate_script,
    resolve_api_profile,
    tcode_api_compat_context,
)
from tcode_api.schemas.base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1
from tcode_api.types import identity_transform


class TestTCodeAPI(unittest.TestCase):
    """Test that all entities in the tcode_api.api package are correctly represented in the API history log."""

    def _get_most_recent_api_profile(self, compat_context: CompatContext) -> dict[str, int]:
        """Helper method to get the most recent API profile from the compat context."""
        api_version_str = compat_context.api_history_log.get_most_recent_version()
        return resolve_api_profile(api_version_str, compat_context)

    # @connor not running this method yet, mostly a concept that I might get working later.
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

    def _get_tcode_api_versioned_models(self) -> list[tuple[str, type[BaseSchemaVersionedModelV1]]]:
        """Dynamically find all of the schema_versioned models in the tcode_api.api package.

        :note: Some exposed entities in tcode_api are unversioned and are expected to not be in the
            API profile. We exclude those here. (ex. TrajectoryType (enum), LabwareDescription (union))
        """
        tc_classes = inspect.getmembers(tc, inspect.isclass)
        retval = []
        for name, cls in tc_classes:
            if not issubclass(cls, BaseSchemaVersionedModelV1):
                continue
            retval.append((name, cls))
        return retval

    def test_schema_registry_matches_history_log(
        self, compat_context: CompatContext = tcode_api_compat_context
    ) -> None:
        """Test that all entities in the tcode_api.api package have their current schema_version represented in the API history log."""
        api_versioned_entities = self._get_tcode_api_versioned_models()
        profile = self._get_most_recent_api_profile(compat_context)

        @dataclasses.dataclass
        class SchemaVersionMismatchReport:
            """Stores metadata about a schema whose schema_version doesn't match that of tcode-api.api."""

            compat_context_name: str
            """Name of the CompatContext containing the mismatch."""

            schema_name: str
            """Name of the schema with the mismatch."""

            cls_schema_version: int
            """The schema_version of the entity as defined in a file in tcode_api.schemas and
            registered with compat_context.schema_registry."""

            api_schema_version: int
            """The schema_version of the entity in the most modern semver available in compat_context.api_history_log."""

        entities_missing_from_profile: list[str] = []
        entites_with_schema_version_mismatch_w_profile: list[SchemaVersionMismatchReport] = []
        for name, cls in api_versioned_entities:
            cls_schema_version = cls.model_fields["schema_version"].default
            try:
                api_schema_version = profile[name]
                if cls_schema_version != api_schema_version:
                    entites_with_schema_version_mismatch_w_profile.append(
                        SchemaVersionMismatchReport(
                            compat_context_name=compat_context.api_history_log.name,
                            schema_name=name,
                            cls_schema_version=cls_schema_version,
                            api_schema_version=api_schema_version,
                        )
                    )
            except KeyError:
                entities_missing_from_profile.append(name)

        if (
            len(entities_missing_from_profile) > 0
            or len(entites_with_schema_version_mismatch_w_profile) > 0
        ):
            error_message = "The following entities have mismatches between their schema_version and the API history log:\n"
            if len(entities_missing_from_profile) > 0:
                error_message += f"Entities missing from API history log profile: {entities_missing_from_profile}\n"
            if len(entites_with_schema_version_mismatch_w_profile) > 0:
                for report in entites_with_schema_version_mismatch_w_profile:
                    error_message += (
                        f"Entity '{report.schema_name}' has schema_version {report.cls_schema_version} in the code but "
                        f"{report.api_schema_version} in the API history log for compat context '{report.compat_context_name}'.\n"
                    )
            self.fail(error_message)

    def test_tcode_api_entities_match_compat_context(self) -> None:
        """Test that all entities in the tcode_api.api package are represented in the API history log."""
        from tcode_api.api.compat import tcode_api_compat_context  # noqa: PLC0415

        api_versioned_entity_names = [name for name, cls in self._get_tcode_api_versioned_models()]

        profile = self._get_most_recent_api_profile(tcode_api_compat_context)
        missing_from_profile = [name for name in api_versioned_entity_names if name not in profile]
        if len(missing_from_profile) > 0:
            self.fail(
                f"The following entities are `schema_version`ed entities exposed in tcode_api.api but not represented in the API history log for the most recent version: {missing_from_profile}"
            )


class TestPauseV1ToV2Migration(unittest.TestCase):
    """Regression tests for the PAUSE v1->v2 migration (added in tcode-api v1.39.0)."""

    def test_migrate_pause_v1_with_robot_id(self) -> None:
        """A v1 PAUSE payload that already carries a ``robot_id`` migrates to v2."""
        data = {"type": "PAUSE", "schema_version": 1, "robot_id": "robot-a"}
        migrated = migrate_data_to_latest(data=data, schema_name="PAUSE")
        self.assertEqual(migrated["schema_version"], 2)
        self.assertEqual(migrated["robot_id"], "robot-a")

    def test_migrate_pause_v1_without_robot_id_raises(self) -> None:
        """A v1 PAUSE payload missing ``robot_id`` cannot be auto-migrated."""
        data = {"type": "PAUSE", "schema_version": 1}
        with self.assertRaises(ValueError):
            migrate_data_to_latest(data=data, schema_name="PAUSE")


class TestSendWebhookV1ToV2Migration(unittest.TestCase):
    """Regression tests for the SEND_WEBHOOK v1->v2 migration (added in tcode-api v1.50.0)."""

    def test_migrate_send_webhook_v1_with_module_id(self) -> None:
        """A v1 SEND_WEBHOOK payload that already carries a ``module_id`` migrates to v2."""
        data = {
            "type": "SEND_WEBHOOK",
            "schema_version": 1,
            "module_id": "magdeck-1",
            "pause_execution": False,
            "url": "https://example.invalid/hook",
        }
        migrated = migrate_data_to_latest(data=data, schema_name="SEND_WEBHOOK")
        self.assertEqual(migrated["schema_version"], 2)
        self.assertEqual(migrated["module_id"], "magdeck-1")
        self.assertEqual(migrated["url"], "https://example.invalid/hook")

    def test_migrate_send_webhook_v1_without_module_id_raises(self) -> None:
        """A v1 SEND_WEBHOOK names no module, and one cannot be inferred."""
        data = {
            "type": "SEND_WEBHOOK",
            "schema_version": 1,
            "pause_execution": False,
            "url": "https://example.invalid/hook",
        }
        with self.assertRaises(ValueError):
            migrate_data_to_latest(data=data, schema_name="SEND_WEBHOOK")


class TestLabwareHolderModuleIdWidening(unittest.TestCase):
    """Regression tests for ModuleId joining the LabwareHolder union (tcode-api v1.51.0).

    .. note:: Generated by Claude Opus 5.

    The union widened, so the three commands carrying a LabwareHolder each bumped. Nothing
    about an older payload changed, which is exactly what these assert: every pre-bump holder
    still validates, and the migrators only move the version.
    """

    DECK_SLOT_HOLDER = {
        "type": "LabwareHolderName",
        "schema_version": 1,
        "robot_id": "robot-a",
        "name": "DeckSlot_1",
    }

    def test_put_down_labware_v1_migrates(self) -> None:
        data = {
            "type": "PUT_DOWN_LABWARE",
            "schema_version": 1,
            "robot_id": "robot-a",
            "holder": self.DECK_SLOT_HOLDER,
        }
        migrated = migrate_data_to_latest(data=data, schema_name="PUT_DOWN_LABWARE")
        self.assertEqual(migrated["schema_version"], 2)
        self.assertEqual(migrated["holder"], self.DECK_SLOT_HOLDER)
        self.assertIsInstance(load_api_object(migrated), tc.PUT_DOWN_LABWARE)

    def test_remove_labware_lid_v2_migrates(self) -> None:
        data = {
            "type": "REMOVE_LABWARE_LID",
            "schema_version": 2,
            "robot_id": "robot-a",
            "labware_id": "plate-1",
            "storage_holder": self.DECK_SLOT_HOLDER,
        }
        migrated = migrate_data_to_latest(data=data, schema_name="REMOVE_LABWARE_LID")
        self.assertEqual(migrated["schema_version"], 3)
        self.assertEqual(migrated["storage_holder"], self.DECK_SLOT_HOLDER)
        self.assertIsInstance(load_api_object(migrated), tc.REMOVE_LABWARE_LID)

    def test_a_module_is_a_valid_holder(self) -> None:
        """What the widening is for: a command can name a module as the destination."""
        command = tc.PUT_DOWN_LABWARE(robot_id="robot-a", holder=tc.ModuleId(id="magdeck-1"))
        self.assertIsInstance(command.holder, tc.ModuleId)
        rebuilt = tc.PUT_DOWN_LABWARE.model_validate(command.model_dump())
        assert isinstance(rebuilt.holder, tc.ModuleId)  # narrow for mypy
        self.assertEqual(rebuilt.holder.id, "magdeck-1")


class TestAddModuleToRegisterModuleMigration(unittest.TestCase):
    """Regression tests for the ADD_MODULE -> REGISTER_MODULE rename (tcode-api v1.51.0).

    .. note:: Generated by Claude Opus 5.

    The rename is recorded in ``APIHistoryLog.migrations``; the field change it carries
    (``descriptor`` -> ``description``) is REGISTER_MODULE's own v1->v2 migrator. A payload
    therefore crosses both in one call.
    """

    LOCATION = {
        "type": "LocationAsLabwareHolder",
        "schema_version": 1,
        "robot_id": "robot-a",
        "labware_holder_name": "DeckSlot_3",
    }

    def _full_descriptor(self) -> dict:
        """A v1 descriptor that happens to specify everything a description requires.

        .. note:: Generated by Claude Opus 5.
        """
        return {
            "type": "Module",
            "schema_version": 1,
            "x_length": {"magnitude": 127.76, "units": "mm"},
            "y_length": {"magnitude": 85.48, "units": "mm"},
            "z_length": {"magnitude": 20.0, "units": "mm"},
            "pinchable": False,
            "holder_transform": identity_transform(),
            "supports_liftable_labware": True,
        }

    def test_fully_specified_descriptor_migrates(self) -> None:
        """An ADD_MODULE whose descriptor leaves nothing out becomes a REGISTER_MODULE v2."""
        data = {
            "type": "ADD_MODULE",
            "schema_version": 1,
            "id": "magdeck-1",
            "descriptor": self._full_descriptor(),
            "location": self.LOCATION,
        }
        migrated = migrate_data_to_latest(data=data, schema_name="ADD_MODULE")
        self.assertEqual(migrated["type"], "REGISTER_MODULE")
        self.assertEqual(migrated["schema_version"], 2)
        self.assertEqual(migrated["id"], "magdeck-1")
        self.assertNotIn("descriptor", migrated)
        self.assertEqual(migrated["description"]["holder_transform"], identity_transform())

    def test_migrated_payload_builds(self) -> None:
        """The migrated form validates, which is what the rename is ultimately for."""
        data = {
            "type": "ADD_MODULE",
            "schema_version": 1,
            "id": "magdeck-1",
            "descriptor": self._full_descriptor(),
            "location": self.LOCATION,
        }
        command = load_api_object(migrate_data_to_latest(data=data, schema_name="ADD_MODULE"))
        self.assertIsInstance(command, tc.REGISTER_MODULE)
        assert isinstance(command, tc.REGISTER_MODULE)  # narrow for mypy
        self.assertEqual(command.description.supports_liftable_labware, True)

    def test_partial_descriptor_raises(self) -> None:
        """A descriptor that omitted fields has no source for them; v1 expected resolution."""
        descriptor = self._full_descriptor()
        del descriptor["supports_liftable_labware"]
        data = {
            "type": "ADD_MODULE",
            "schema_version": 1,
            "id": "magdeck-1",
            "descriptor": descriptor,
            "location": self.LOCATION,
        }
        with self.assertRaises(ValueError) as ctx:
            migrate_data_to_latest(data=data, schema_name="ADD_MODULE")
        self.assertIn("supports_liftable_labware", str(ctx.exception))


class TestAddPipetteTipGroupV1ToV2Migration(unittest.TestCase):
    """Regression tests for the ADD_PIPETTE_TIP_GROUP v1->v2 migration (added in tcode-api v1.39.0)."""

    def _v1_payload(self) -> dict:
        return {
            "type": "ADD_PIPETTE_TIP_GROUP",
            "schema_version": 1,
            "id": "tips-a",
            "descriptor": {},
        }

    def test_migrate_add_pipette_tip_group_v1_with_robot_id(self) -> None:
        """A v1 ADD_PIPETTE_TIP_GROUP payload that already carries a ``robot_id`` migrates to v2."""
        data = {**self._v1_payload(), "robot_id": "robot-a"}
        migrated = migrate_data_to_version(
            data=data, schema_name="ADD_PIPETTE_TIP_GROUP", target_version=2
        )
        self.assertEqual(migrated["schema_version"], 2)
        self.assertEqual(migrated["robot_id"], "robot-a")

    def test_migrate_add_pipette_tip_group_v1_without_robot_id_raises(self) -> None:
        """A v1 ADD_PIPETTE_TIP_GROUP payload missing ``robot_id`` cannot be auto-migrated."""
        with self.assertRaises(ValueError):
            migrate_data_to_latest(data=self._v1_payload(), schema_name="ADD_PIPETTE_TIP_GROUP")


class TestLabwarePinchableV3ToV4Migration(unittest.TestCase):
    """Regression tests for the labware v3->v4 migration adding `pinchable` (tcode-api v1.42.0)."""

    def test_migrate_lid_v3_backfills_pinchable_true(self) -> None:
        """A v3 Lid payload with no `pinchable` backfills as pinchable=True (lids are pinched)."""
        data = {"type": "Lid", "schema_version": 3}
        migrated = migrate_data_to_latest(data=data, schema_name="Lid")
        self.assertEqual(migrated["schema_version"], 4)
        self.assertTrue(migrated["pinchable"])

    def test_migrate_lid_v3_preserves_explicit_pinchable(self) -> None:
        """A v3 Lid payload that already sets `pinchable` keeps that value."""
        data = {"type": "Lid", "schema_version": 3, "pinchable": False}
        migrated = migrate_data_to_latest(data=data, schema_name="Lid")
        self.assertEqual(migrated["schema_version"], 4)
        self.assertFalse(migrated["pinchable"])

    def test_migrate_well_plate_v3_backfills_pinchable_true(self) -> None:
        """A v3 WellPlate payload with no `pinchable` backfills as pinchable=True (well plates are
        pinched)."""
        data = {"type": "WellPlate", "schema_version": 3}
        migrated = migrate_data_to_version(data=data, target_version=4, schema_name="WellPlate")
        self.assertEqual(migrated["schema_version"], 4)
        self.assertTrue(migrated["pinchable"])

    def test_migrate_well_plate_v3_migrates_nested_lid(self) -> None:
        """A v3 WellPlate payload with a nested v3 lid also migrates the nested lid to v4."""
        data = {
            "type": "WellPlate",
            "schema_version": 3,
            "lid": {"type": "Lid", "schema_version": 3},
        }
        migrated = migrate_data_to_version(data=data, target_version=4, schema_name="WellPlate")
        self.assertEqual(migrated["schema_version"], 4)
        self.assertTrue(migrated["pinchable"])
        self.assertEqual(migrated["lid"]["schema_version"], 4)
        self.assertTrue(migrated["lid"]["pinchable"])

    def test_migrate_well_plate_v3_without_lid(self) -> None:
        """A v3 WellPlate payload with no lid migrates without adding one."""
        data = {"type": "WellPlate", "schema_version": 3, "lid": None}
        migrated = migrate_data_to_version(data=data, target_version=4, schema_name="WellPlate")
        self.assertEqual(migrated["schema_version"], 4)
        self.assertIsNone(migrated["lid"])

    def test_migrate_trash_v3_backfills_pinchable_false(self) -> None:
        """A v3 Trash payload with no `pinchable` backfills as pinchable=False (trash bins are
        lifted)."""
        data = {"type": "Trash", "schema_version": 3}
        migrated = migrate_data_to_latest(data=data, schema_name="Trash")
        self.assertEqual(migrated["schema_version"], 4)
        self.assertFalse(migrated["pinchable"])

    def test_migrate_tube_holder_v3_backfills_pinchable_false(self) -> None:
        """A v3 TubeHolder payload with no `pinchable` backfills as pinchable=False (tube holders
        are lifted)."""
        data = {"type": "TubeHolder", "schema_version": 3}
        migrated = migrate_data_to_latest(data=data, schema_name="TubeHolder")
        self.assertEqual(migrated["schema_version"], 4)
        self.assertFalse(migrated["pinchable"])

    def test_migrate_pipette_tip_box_v3_backfills_pinchable_false(self) -> None:
        """A v3 PipetteTipBox payload with no `pinchable` backfills as pinchable=False (pipette
        tip boxes are lifted)."""
        data = {"type": "PipetteTipBox", "schema_version": 3}
        migrated = migrate_data_to_latest(data=data, schema_name="PipetteTipBox")
        self.assertEqual(migrated["schema_version"], 4)
        self.assertFalse(migrated["pinchable"])


class TestRealNestedMigration(unittest.TestCase):
    """Nested migration against the real tcode-api schemas."""

    def test_create_labware_migrates_nested_trash(self) -> None:
        """A CREATE_LABWARE from tcode-api 1.40.0 holding a v3 Trash description gets the Trash
        migrated to v4, which backfills `pinchable`."""

        def mm(magnitude: float) -> dict:
            return {"type": "ValueWithUnits", "magnitude": magnitude, "units": "mm"}

        def ul(magnitude: float) -> dict:
            return {"type": "ValueWithUnits", "magnitude": magnitude, "units": "uL"}

        command = {
            "type": "CREATE_LABWARE",
            "robot_id": "robot",
            "holder": {"type": "LabwareHolderName", "robot_id": "robot", "name": "DeckSlot_1"},
            "description": {
                "type": "Trash",
                "schema_version": 3,
                "id": "trash",
                "name": "Trash Bin",
                "x_length": mm(127.76),
                "y_length": mm(85.48),
                "z_length": mm(75),
                "depth": mm(71.66),
                "grid": {
                    "row_count": 1,
                    "column_count": 1,
                    "row_pitch": mm(0),
                    "column_pitch": mm(0),
                    "row_offset": mm(0),
                    "column_offset": mm(0),
                },
                "well": {
                    "depth": mm(72),
                    "shape": {
                        "type": "AxisAlignedRectangle",
                        "x_length": mm(121.5),
                        "y_length": mm(79.25),
                    },
                    "bottom_shape": {"type": "Flat"},
                    "min_volume": ul(0),
                    "max_volume": ul(693279),
                },
            },
        }
        inst = load_api_object(data=command, api_version="1.40.0")
        self.assertIsInstance(inst, tc.CREATE_LABWARE)
        description = inst.description  # type: ignore [attr-defined]
        self.assertIsInstance(description, tc.TrashDescription)
        self.assertEqual(
            description.schema_version, 4
        )  # NOTE: Bump this when you bump the schema version of TrashDescription
        self.assertFalse(description.pinchable)


class TestReadAndMigrateScript(unittest.TestCase):
    """Tests for the ``read_and_migrate_script`` function."""

    def test_read_and_migrate_script(self) -> None:
        """A real script from tcode-api 1.40.0 migrates to the latest version without error.

        We don't inspect the result, other than to check that it's not empty, so that the test will
        keep working as we bump schemas.
        """
        path = Path(__file__).parent / "migrator_test.tc"
        json_str = path.read_text()
        script = read_and_migrate_script(json_str)
        self.assertIsInstance(script, tc.TCodeScript)
        self.assertGreater(len(script.commands), 0)


class TestCalibrateLabwareWellCenterV1(unittest.TestCase):
    """Regression tests for CALIBRATE_LABWARE_WELL_CENTER v1 (added in tcode-api v1.49.0)."""

    def test_v1_payload_validates_and_is_in_api_profile(self) -> None:
        """A v1 payload validates against the schema and appears in the API profile."""
        profile = resolve_api_profile("v1.49.0", tcode_api_compat_context)
        self.assertEqual(profile["CALIBRATE_LABWARE_WELL_CENTER"], 1)
        data = {
            "type": "CALIBRATE_LABWARE_WELL_CENTER",
            "schema_version": 1,
            "robot_id": "test-robot-id",
            "location": {
                "type": "LocationAsLabwareIndex",
                "schema_version": 1,
                "labware_id": "test-labware-id",
                "location_index": 0,
                "well_part": "BOTTOM",
            },
            "persistent": False,
        }
        command = tc.CALIBRATE_LABWARE_WELL_CENTER.model_validate(data)
        self.assertTrue(command.modify_all_wells)
        self.assertEqual(command.location.location_index, 0)

    def test_v1_rejects_location_relative_to_labware(self) -> None:
        """`LocationRelativeToLabware` carries no well index, so it must not validate."""
        data = {
            "type": "CALIBRATE_LABWARE_WELL_CENTER",
            "schema_version": 1,
            "robot_id": "test-robot-id",
            "location": {
                "type": "LocationRelativeToLabware",
                "schema_version": 1,
                "labware_id": "test-labware-id",
                "transform": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
            },
            "persistent": False,
        }
        with self.assertRaises(ValidationError):
            tc.CALIBRATE_LABWARE_WELL_CENTER.model_validate(data)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    unittest.main()
