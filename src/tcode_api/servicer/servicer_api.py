"""TCode servicer API request-response structures."""

from typing import Annotated, Any, Mapping, MutableMapping, Self, TypeAlias

from pydantic import BaseModel, Field, field_serializer

import tcode_api.api as tc
from tcode_api.error import TCodeResultReport
from tcode_api.types import CommandID, Matrix, identity_transform
from tcode_api.utilities import generate_id

RawCommandData: TypeAlias = Annotated[
    Mapping[str, Any],
    Field(
        description="Raw tcode-api schema; will be migrated (if necessary) on load. See ``tcode_api.TCode`` for full structure example.",
        examples=[
            tc.MOVE_TO_LOCATION(
                type="MOVE_TO_LOCATION",
                schema_version=2,
                robot_id=generate_id(),
                location=tc.LocationAsLabwareIndex(
                    type="LocationAsLabwareIndex",
                    schema_version=1,
                    labware_id=generate_id(),
                    location_index=0,
                    well_part=tc.WellPartType.BOTTOM,
                ),
                location_offset=identity_transform(),
                flange=None,
                flange_offset=identity_transform(),
                path_type=None,
                trajectory_type=None,
                speed=None,
            ).model_dump()
        ],
    ),
]


class Result(BaseModel):
    """Result object for standardizing display of successes and failures."""

    success: bool
    code: str
    message: str | None = None
    details: dict | None = None

    @classmethod
    def from_tcode_result_report_interface(cls, result_report: TCodeResultReport) -> Self:
        return cls(
            success=result_report.success,
            code=result_report.code,
            message=result_report.message,
            details=result_report.details,
        )

    @field_serializer("details")
    def serialize_details(self, details: dict | None, info) -> dict | None:
        """Custom serializer for details field to avoid serialization issues on 'pint.Quantity' objects."""
        if details is None:
            return None
        serialized_details = {}
        for key, value in details.items():
            serialized_details[key] = str(value)
        return serialized_details


class DiscoverFleetRequest(BaseModel):
    """Request object for discover_fleet endpoint."""

    robot_serial_numbers: list[str] = Field(
        default_factory=list,
        description="List of robot serial numbers to discover. If empty, all robots will be discovered.",
        examples=[["T0001V0105F01L00N0001", "T0001V0105F01L00N0002"]],
    )


class DiscoverFleetResponse(BaseModel):
    """Response object for discover_fleet endpoint."""


class CanmeraConnectWifiRequest(BaseModel):
    """Request to provision a robot's CAN bus camera (canmera) WiFi and connect it.

    Runs over the CAN bus, so it works before the camera node has any network access.

    :param robot_id: target robot ID
    """

    robot_id: str
    ssid: str = Field(min_length=1, description="WiFi network name to join.")
    password: str = Field(min_length=8, description="WiFi password (WPA2 minimum length).")


class CanmeraConnectWifiResponse(BaseModel):
    """Response from connecting a canmera to WiFi.

    :param ip: IP address the camera node reported after joining, when successful
    :param result: Response metadata
    """

    ip: str | None = None
    result: Result


class CanmeraStatusRequest(BaseModel):
    """Request for a robot's CAN bus camera (canmera) health flags and network status.

    :param robot_id: target robot ID
    """

    robot_id: str


class CanmeraStatusResponse(BaseModel):
    """Response with a canmera's health flags and network status.

    Queried over the CAN bus, so it works before the camera node has any network
    access. The network fields are null until the node has joined WiFi.
    """

    camera_ok: bool = False
    streaming: bool = False
    wifi_connected: bool = False
    robot_name_set: bool = False
    recording: bool = False
    ssid: str | None = None
    hostname: str | None = None
    ip: str | None = None
    result: Result


class ClearScheduleResponse(BaseModel):
    """Response object for clear_schedule endpoint."""

    cleared_commands: list[tc.TCode]


class RobotStatusDetail(BaseModel):
    """Per-robot status information."""

    robot_id: str
    command_id: CommandID | None
    queue_depth: int
    run_state: bool
    result: Result


class GetStatusResponse(BaseModel):
    """Response object for get_status endpoint."""

    command_id: CommandID | None
    operation_count: int
    run_state: bool
    result: Result
    robots: list[RobotStatusDetail] = Field(default_factory=list)


class ScheduleCommandRequest(BaseModel):
    """Request object for the schedule_command endpoint.

    :param command_id: Unique identifier for this scheduled command (envelope-level).
    :param command: The raw TCode command payload.
    :param depends_on: Command IDs that must complete before this command executes.
    :param sync_group: Command IDs of peer commands that must be at the head of their
        respective robot queues (with satisfied dependencies) before this command proceeds.
    """

    command_id: CommandID
    command: RawCommandData
    depends_on: list[CommandID] = Field(default_factory=list)
    sync_group: list[CommandID] = Field(default_factory=list)


class ScheduleCommandResponse(BaseModel):
    """Response object for the schedule_command endpoint."""

    state: MutableMapping[
        str, Any
    ]  # A serialized FleetStateSnapshot, cannot use directly due to pyrsistent implementation
    result: Result


class ScheduleCommandsRequest(BaseModel):
    """Request object for the schedule_commands endpoint."""

    commands: list[ScheduleCommandRequest]


class EnterTeachModeRequest(BaseModel):
    """Request to enter teach mode.

    :param robot_id: target robot ID
    """

    robot_id: str


class EnterTeachModeResponse(BaseModel):
    """Response from entering teach mode.

    :param result: Response metadata
    """

    result: Result


class ExitTeachModeRequest(BaseModel):
    """Request to exit teach mode, saving current location.

    :param robot_id: target robot ID
    """

    robot_id: str


class ExitTeachModeResponse(BaseModel):
    """Response from exiting teach mode.

    :param result: Response metadata
    :param transform: transformation matrix of tool control point relative to robot base.
    """

    result: Result
    transform: Matrix


class SerialNumberLookupRequest(BaseModel):
    """tcode-servicer serial_number_lookup endpoint request data structure."""

    ids: list[str] = Field(
        description="IDs to look up. Interpreted as referencing an entity with a SerialNumber (ex. a robot or tool)",
    )


class SerialNumberLookupResult(BaseModel):
    """Individual result entry for a single ID lookup in the serial_number_lookup endpoint."""

    serial_number: str | None = Field(
        default=None,
        description="Resolved serial number, or null if resolution failed for any reason (including not found).",
        examples=["T0004V0102F01L00N0001", "T0001V0105F01L00N0001", None],
    )
    result: Result = Field(
        description="Result of the lookup attempt, including success status and error details if applicable.",
    )


class SerialNumberLookupResponse(BaseModel):
    """tcode-servicer serial_number_lookup endpoint response data structure."""

    results: dict[str, SerialNumberLookupResult] = Field(
        description="Mapping of input IDs to their corresponding lookup results, including resolved serial numbers and result metadata.",
    )


class TCodeCommandSchedulingReport(BaseModel):
    """Report from a single TCode command scheduling call."""

    command_id: CommandID
    command: tc.TCode
    result: Result
    duration: float


class TCodeSchedulingReport(BaseModel):
    """Report of a TCodeScript scheduling session."""

    command_reports: list[TCodeCommandSchedulingReport]
    start_time: str
    end_time: str
