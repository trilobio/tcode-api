"""TCode servicer API request-response structures."""

from typing import Any, MutableMapping, Self

from pydantic import BaseModel, field_serializer

import tcode_api.api as tc
from tcode_api.error import TCodeResultReport
from tcode_api.types import CommandID, Matrix

# Response structures #


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


class ClearScheduleResponse(BaseModel):
    """Response object for clear_schedule endpoint."""

    cleared_commands: list[tc.TCode]


class GetStatusResponse(BaseModel):
    """Response object for get_status endpoint."""

    command_id: CommandID | None
    operation_count: int
    run_state: bool
    result: Result


class ScheduleCommandRequest(BaseModel):
    """Request object for the schedule_command endpoint."""

    command_id: CommandID
    command: tc.TCode


class ScheduleCommandResponse(BaseModel):
    """Response object for the schedule_command endpoint."""

    state: MutableMapping[
        str, Any
    ]  # A serialized FleetStateSnapshot, cannot use directly due to pyrsistent implementation
    result: Result


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
