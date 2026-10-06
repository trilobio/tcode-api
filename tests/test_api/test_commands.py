"""tcode_api.api.commands unittests."""

import datetime
import logging
import math
import unittest
from importlib.metadata import version
from typing import get_args

# Using the below import style because it's how we expect users to import tcode_api
import tcode_api.api as tc
from tcode_api.schemas.commands.base.robot_specific_tcode_command.v1 import (
    BaseRobotSpecificTCodeCommandV1,
)
from tcode_api.schemas.commands.base.tcode_command.v1 import BaseTCodeCommandV1
from tcode_api.servicer.servicer_api import (
    GetStatusResponse,
    Result,
    RobotStatusDetail,
)
from tcode_api.types import identity_transform
from tcode_api.utilities import create_transform, mm, rad

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
                tcode_api_version=version("tcode_api"),
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
        ENDPOINTS_TO_SKIP = [BaseRobotSpecificTCodeCommandV1]
        endpoints = [
            obj
            for obj in tc.__dict__.values()
            if hasattr(obj, "__bases__")
            and (
                BaseTCodeCommandV1 in obj.__bases__
                or BaseRobotSpecificTCodeCommandV1 in obj.__bases__
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


class TestGetStatusResponseMock(unittest.TestCase):
    """Tests for the `mock` bit on GetStatusResponse."""

    def _response(self, **kwargs) -> "GetStatusResponse":
        return GetStatusResponse(
            command_id=None,
            operation_count=0,
            run_state=False,
            result=Result(success=True, code="success"),
            **kwargs,
        )

    def test_defaults_to_false(self) -> None:
        """A server that does not report the bit is assumed to drive real hardware."""
        self.assertFalse(self._response().mock)

    def test_round_trips(self) -> None:
        """The bit survives serialize -> deserialize."""
        response = self._response(mock=True)
        self.assertTrue(GetStatusResponse.model_validate(response.model_dump()).mock)


class TestRobotStatusDetailSerialNumber(unittest.TestCase):
    """Tests for the physical serial number on RobotStatusDetail."""

    def _detail(self, **kwargs) -> "RobotStatusDetail":
        return RobotStatusDetail(
            robot_id="robot-a",
            command_id=None,
            queue_depth=0,
            run_state=False,
            result=Result(success=True, code="success"),
            **kwargs,
        )

    def test_defaults_to_none(self) -> None:
        """A robot whose physical serial has not been resolved reports None."""
        self.assertIsNone(self._detail().serial_number)

    def test_round_trips(self) -> None:
        """A resolved serial survives serialize -> deserialize."""
        detail = self._detail(serial_number="T0001V0105F00L00N0004")
        reloaded = RobotStatusDetail.model_validate(detail.model_dump())
        self.assertEqual(reloaded.serial_number, "T0001V0105F00L00N0004")


class TestRegisterModule(unittest.TestCase):
    """Tests for REGISTER_MODULE, which builds a module from its description and ids it.

    .. note:: Generated by Claude Opus 5.
    """

    def _description(self) -> tc.ModuleDescription:
        """A module is never resolved, so every field it needs is supplied up front.

        .. note:: Generated by Claude Opus 5.
        """
        return tc.ModuleDescription(
            x_length=mm(127.76),
            y_length=mm(85.48),
            z_length=mm(20.0),
            pinchable=False,
            holder_transform=create_transform(z=mm(12.5)),
            supports_liftable_labware=True,
        )

    def test_deck_slot_location(self) -> None:
        """A module sitting in a deck slot is located by labware holder name."""
        command = tc.REGISTER_MODULE(
            id="magdeck-1",
            description=self._description(),
            location=tc.LocationAsLabwareHolder(
                robot_id="robot-a", labware_holder_name="DeckSlot_3"
            ),
        )
        self.assertIsInstance(command.location, tc.LocationAsLabwareHolder)
        assert isinstance(command.location, tc.LocationAsLabwareHolder)  # narrow for mypy
        self.assertEqual(command.location.labware_holder_name, "DeckSlot_3")

    def test_fixed_location(self) -> None:
        """A module bolted down is located by a transform relative to the robot's root."""
        command = tc.REGISTER_MODULE(
            id="shaker-1",
            description=self._description(),
            location=tc.LocationRelativeToRobot(
                robot_id="robot-a",
                matrix=create_transform(x=mm(100.0), a=rad(math.pi / 2)),
            ),
        )
        self.assertIsInstance(command.location, tc.LocationRelativeToRobot)
        assert isinstance(command.location, tc.LocationRelativeToRobot)  # narrow for mypy
        self.assertEqual(command.location.matrix[0][3], 0.1)  # 100 mm, in metres

    def test_location_is_discriminated(self) -> None:
        """Only the two module location types are accepted."""
        payload = {
            "type": "REGISTER_MODULE",
            "schema_version": 2,
            "id": "magdeck-1",
            "description": self._description().model_dump(),
            "location": tc.LocationRelativeToWorld(matrix=identity_transform()).model_dump(),
        }
        with self.assertRaises(ValueError):
            tc.REGISTER_MODULE.model_validate(payload)

    def test_location_is_required(self) -> None:
        """A module must say where it is."""
        payload = {
            "type": "REGISTER_MODULE",
            "schema_version": 2,
            "id": "magdeck-1",
            "description": self._description().model_dump(),
        }
        with self.assertRaises(ValueError):
            tc.REGISTER_MODULE.model_validate(payload)

    def test_a_partial_description_is_rejected(self) -> None:
        """The point of taking a description: nothing fills in what the caller left out."""
        payload = {
            "type": "REGISTER_MODULE",
            "schema_version": 2,
            "id": "magdeck-1",
            "description": {"type": "Module", "schema_version": 1, "pinchable": False},
            "location": tc.LocationAsLabwareHolder(
                robot_id="robot-a", labware_holder_name="DeckSlot_3"
            ).model_dump(),
        }
        with self.assertRaises(ValueError):
            tc.REGISTER_MODULE.model_validate(payload)


class TestSendWebhookTargetsModule(unittest.TestCase):
    """SEND_WEBHOOK is addressed to a module, not a robot."""

    def _webhook(self, **kwargs) -> tc.SEND_WEBHOOK:
        return tc.SEND_WEBHOOK(pause_execution=False, url="https://example.invalid/hook", **kwargs)

    def test_module_id_is_required(self) -> None:
        """A webhook with no module has no queue to execute from."""
        payload = {
            "type": "SEND_WEBHOOK",
            "schema_version": 2,
            "pause_execution": False,
            "url": "https://example.invalid/hook",
        }
        with self.assertRaises(ValueError):
            tc.SEND_WEBHOOK.model_validate(payload)

    def test_round_trips(self) -> None:
        """module_id survives serialize -> deserialize."""
        command = self._webhook(module_id="magdeck-1")
        self.assertEqual(
            tc.SEND_WEBHOOK.model_validate(command.model_dump()).module_id, "magdeck-1"
        )

    def test_carries_no_robot_id(self) -> None:
        """A webhook does not occupy a robot; ordering against robot work is the
        schedule envelope's job via depends_on / sync_group."""
        self.assertNotIn("robot_id", tc.SEND_WEBHOOK.model_fields)
