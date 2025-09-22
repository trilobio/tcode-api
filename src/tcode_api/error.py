"""Errors and relevant metadata raised for TCode endpoints.

Resources:
    When to declare custom exceptions: https://stackoverflow.com/q/57165380
    Exceptions vs. result structures: https://softwareengineering.stackexchange.com/a/405074
"""

import enum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field


class _TCodeResultReportBase(BaseModel):
    """Interface for returning results through TCode API for successful and failed operations."""

    type: str
    success: bool  # True if the operation was successful, False otherwise
    details: dict  # Machine-readable details about the error
    message: str  # Human-readable error message
    # code: str  # Domain-specific error code - defined in subclasses


# Validator


class ValidatorErrorCode(enum.StrEnum):
    """Domain-specific error code expected from TCode validation."""

    EMPTY_DECK_SLOT_NOT_FOUND = "empty_deck_slot_not_found"
    EMPTY_PIPETTE_TIP_GROUP = "empty_pipette_tip_group"
    EMPTY_TOOL_HOLDER_NOT_FOUND = "empty_tool_holder_not_found"
    ID_EXISTS = "id_exists"
    ID_NOT_FOUND = "id_not_found"
    INTERNAL_ERROR = "internal_error"
    JOINT_COUNT_MISMATCH = "joint_count_mismatch"
    LID_NOT_FOUND = "lid_not_found"
    TRANSFORM_SIZE_LIMIT_EXCEEDED = "transform_size_limit_exceeded"
    NO_LID_SUPPORT = "no_lid_support"
    NOT_IMPLEMENTED = "not_implemented"
    PIPETTE_TIP_GROUP_DISCARDED = "pipette_tip_group_discarded"
    PIPETTE_TIP_GROUP_NOT_FOUND = "pipette_tip_group_not_found"
    PIPETTE_TIP_NOT_MOUNTED = "pipette_tip_not_mounted"
    PIPETTE_VOLUME_LIMIT_EXCEEDED = "pipette_volume_limit_exceeded"
    TOOL_NOT_MOUNTED = "tool_not_mounted"
    TRASH_NOT_FOUND = "trash_not_found"
    UNEXPECTED_LABWARE = "unexpected_labware"
    UNEXPECTED_LABWARE_TYPE = "unexpected_labware_type"
    UNEXPECTED_LID = "unexpected_lid"
    UNEXPECTED_PIPETTE_TIP = "unexpected_pipette_tip"
    UNEXPECTED_PIPETTE_TIP_GROUP = "unexpected_pipette_tip_group"
    UNEXPECTED_TOOL = "unexpected_tool"
    UNITS_ERROR = "units_error"
    UNNECESSARY = "unnecessary"
    WRONG_TOOL_MOUNTED = "wrong_tool_mounted"


class ValidatorError(_TCodeResultReportBase):
    """Base class for all tcode.validator errors."""

    type: Literal["ValidatorError"] = "ValidatorError"
    code: ValidatorErrorCode


# Scheduler


class SchedulerCode(enum.StrEnum):
    """Enumeration of the different response codes from the scheduler."""

    SUCCESS = "success"
    NOT_IMPLEMENTED = "not_implemented"


class SchedulerError(_TCodeResultReportBase):
    """Custom exception for the scheduler."""

    type: Literal["SchedulerError"] = "SchedulerError"
    code: SchedulerCode


# Resolver


class ResolverCode(str, enum.Enum):
    """Domain-specific code returned from TCode resolution.

    This code used in conjunction with the ResolverResult object to return fine-grained
    resolution debugging info to the user.
    """

    ID_EXISTS = "id_exists"
    HOLDER_NOT_FOUND = "holder_not_found"
    MULTIPLE_MATCHING_ENTITIES = "multiple_entities"
    NO_DISCOVERED_ENTITIES = "no_discovered_entities"
    NO_MATCHING_ENTITIES = "no_matching_entities"
    NO_UNRESOLVED_ENTITIES = "no_unresolved_entites"
    NOT_IMPLEMENTED = "not_implemented"
    DECK_SLOT_NOT_EMPTY = "deck_slot_not_empty"
    SUCCESS = "success"
    INTERNAL_ERROR = "internal_error"
    LABWARE_HOLDER_NOT_EMPTY = "labware_holder_occupied"
    LABWARE_HOLDER_EMPTY = "labware_holder_empty"
    PLATE_NOT_STACKABLE = "plate_not_stackable"


class ResolverResult(_TCodeResultReportBase):
    """Base class for results returned from the resolver submodule."""

    type: Literal["ResolverResult"] = "ResolverResult"
    code: ResolverCode

    @classmethod
    def ok(cls, message: str = "", details: dict | None = None) -> Self:
        """Create a successful result."""
        details = details or {}
        return cls(
            success=True, code=ResolverCode.SUCCESS, message=message, details=details
        )

    @classmethod
    def error(
        cls, code: ResolverCode, message: str, details: dict | None = None
    ) -> Self:
        """Create a result containing an error. Enforces good exception practices through mandatory args."""
        details = details or {}
        return cls(success=False, code=code, message=message, details=details)


# Executor


class ExecutionCode(enum.StrEnum):
    """Domain-specific code returned from TCode execution.

    This code used in conjunction with the ResolutionResult object to return fine-grained
    resolution debugging info to the user.
    """

    SUCCESS = enum.auto()
    PIPETTE_TIP_DROPOFF_FAILURE = enum.auto()
    ROBOT_BOOT_STATE_FAILURE = enum.auto()
    ROBOT_ESTOPPED = enum.auto()
    INTERNAL_ERROR = enum.auto()


class ExecutionResult(_TCodeResultReportBase):
    """Base class for results returned from the tcode.servicer execution."""

    type: Literal["ExecutionResult"] = "ExecutionResult"
    code: ExecutionCode

    @classmethod
    def ok(cls, details: dict | None = None) -> Self:
        """Create a successful result."""
        details = details or {}
        return cls(
            success=True, code=ExecutionCode.SUCCESS, message="", details=details
        )

    @classmethod
    def error(
        cls, code: ExecutionCode, message: str, details: dict | None = None
    ) -> Self:
        """Create a result containing an error. Enforces good exception practices through mandatory args."""
        details = details or {}
        return cls(success=False, code=code, message=message, details=details)

    def __repr__(self) -> str:
        """Concise string representation of object."""
        inner_str = "ok" if self.success else f"error, code={self.code}"
        return "ExecutionResult(" + inner_str + ")"


TCodeResultReport = Annotated[
    ValidatorError | SchedulerError | ResolverResult | ExecutionResult,
    Field(discriminator="type"),
]
