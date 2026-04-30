"""tcode_api.api.commands unittests."""

import datetime
import logging
import unittest
from typing import get_args

# Using the below import style because it's how we expect users to import tcode_api
import tcode_api.api as tc
from tcode_api.schemas.commands.base import (
    BaseRobotSpecificTCodeCommand,
    BaseTCodeCommand,
)

from .test_base import BaseTestCases


class TestTCodeScript(BaseTestCases.TestBaseSchemaVersionedModel):
    """TCodeScript class unittests."""

    model = tc.TCodeScript

    def _create_valid_model_instance(self) -> tc.TCodeScript:
        """Create a valid TCodeScript instance for testing."""
        return tc.TCodeScript(
            metadata=tc.Metadata(
                name="unittest",
                timestamp=datetime.datetime.now().isoformat(),
                tcode_api_version="0.1.0",
            ),
        )

    def test_instantiate_tcodescript(self) -> None:
        """Ensure that TCodeScript can be instantiated."""
        model = self._create_valid_model_instance()
        self.assertEqual(len(model.commands), 0)

    def test_file_io(self) -> None:
        """Suppress logging during file I/O test."""
        try:
            original_level = logging.getLogger("tcode_api.api.commands").level
            logging.getLogger("tcode_api.api.commands").setLevel(logging.ERROR)
            super().test_file_io()
        finally:
            logging.getLogger("tcode_api.api.commands").setLevel(original_level)


class TestAPI(unittest.TestCase):
    """Various unsorted unittests."""

    def test_descriptors(self) -> None:
        """Ensure that LabwareDescriptors can be instantiated without specifying certain attributes."""
        tc.GripperDescriptor()
        tc.LidDescriptor()
        tc.SingleChannelPipetteDescriptor()
        tc.EightChannelPipetteDescriptor()
        tc.PipetteTipBoxDescriptor()
        tc.ProbeDescriptor()
        tc.RobotDescriptor()
        tc.TrashDescriptor()
        tc.WellPlateDescriptor()


class TestTCodeEndpoints(unittest.TestCase):
    """Mypy-compliant testing to make sure that all endpoints are included in type."""

    def test_endpoints(self) -> None:
        """Test that all endpoints are included in the type."""
        ENDPOINTS_TO_SKIP = [BaseRobotSpecificTCodeCommand]
        endpoints = [
            obj
            for obj in tc.__dict__.values()
            if hasattr(obj, "__bases__")
            and (
                BaseTCodeCommand in obj.__bases__ or BaseRobotSpecificTCodeCommand in obj.__bases__
            )
        ]
        # https://stackoverflow.com/a/64643971
        type_options = get_args(get_args(tc.TCode)[0])
        for endpoint in endpoints:
            if endpoint in ENDPOINTS_TO_SKIP:
                continue
            with self.subTest(endpoint=endpoint):
                self.assertIn(
                    endpoint,
                    type_options,
                    f"\n\nACTION ITEM: Add {endpoint} to tcode_api.api.TCode type",
                )


class TestScheduleCommandRequestSyncFields(unittest.TestCase):
    """Tests for envelope-level depends_on/sync_group on ScheduleCommandRequest.

    These coordination fields live on the schedule envelope, not on the TCode command itself,
    because they reference envelope-level CommandIDs and are only meaningful to the scheduler.
    """

    def _make_command(self) -> dict:
        return tc.COMMENT(type="COMMENT", text="hello").model_dump()

    def test_defaults_are_empty_lists(self) -> None:
        """A request without sync fields has empty defaults."""
        from tcode_api.servicer.servicer_api import ScheduleCommandRequest  # noqa: PLC0415

        req = ScheduleCommandRequest(command_id="cmd-1", command=self._make_command())
        self.assertEqual(req.depends_on, [])
        self.assertEqual(req.sync_group, [])

    def test_sync_fields_round_trip(self) -> None:
        """Populated sync fields survive serialize -> deserialize."""
        from tcode_api.servicer.servicer_api import ScheduleCommandRequest  # noqa: PLC0415

        req = ScheduleCommandRequest(
            command_id="cmd-1",
            command=self._make_command(),
            depends_on=["cmd-0"],
            sync_group=["cmd-2", "cmd-3"],
        )
        restored = ScheduleCommandRequest.model_validate(req.model_dump())
        self.assertEqual(restored.depends_on, ["cmd-0"])
        self.assertEqual(restored.sync_group, ["cmd-2", "cmd-3"])

    def test_sync_fields_json_round_trip(self) -> None:
        """Sync fields survive JSON serialization."""
        from tcode_api.servicer.servicer_api import ScheduleCommandRequest  # noqa: PLC0415

        req = ScheduleCommandRequest(
            command_id="cmd-1",
            command=self._make_command(),
            depends_on=["a", "b"],
            sync_group=["c"],
        )
        restored = ScheduleCommandRequest.model_validate_json(req.model_dump_json())
        self.assertEqual(restored.depends_on, ["a", "b"])
        self.assertEqual(restored.sync_group, ["c"])

    def test_bulk_request_carries_per_entry_sync_fields(self) -> None:
        """ScheduleCommandsRequest.commands is a list of ScheduleCommandRequest envelopes."""
        from tcode_api.servicer.servicer_api import (  # noqa: PLC0415
            ScheduleCommandRequest,
            ScheduleCommandsRequest,
        )

        bulk = ScheduleCommandsRequest(
            commands=[
                ScheduleCommandRequest(command_id="a", command=self._make_command()),
                ScheduleCommandRequest(
                    command_id="b",
                    command=self._make_command(),
                    depends_on=["a"],
                ),
            ]
        )
        restored = ScheduleCommandsRequest.model_validate_json(bulk.model_dump_json())
        self.assertEqual(restored.commands[0].depends_on, [])
        self.assertEqual(restored.commands[1].depends_on, ["a"])
