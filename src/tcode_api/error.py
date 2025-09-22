"""Errors and relevant metadata raised for TCode endpoints.

Resources:
    When to declare custom exceptions: https://stackoverflow.com/q/57165380
    Exceptions vs. result structures: https://softwareengineering.stackexchange.com/a/405074
"""

import enum
from typing import Protocol, Self


class TCodeResultReportInterface(Protocol):
    """Interface for returning results through TCode API for successful and failed operations.
    Any class that exposes this interface can be returned to the API caller.
    """

    success: bool  # True if the operation was successful, False otherwise
    code: str  # Domain-specific error code - verified in unittests
    details: dict  # Machine-readable details about the error
    message: str  # Human-readable error message


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


class ValidatorError(TCodeResultReportInterface, Exception):
    """Base class for all tcode.validator errors."""

    success: bool = False

    def __init__(
        self, message: str, code: ValidatorErrorCode, details: dict | None = None
    ) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}
        self.message = message


# Scheduler


class SchedulerCode(enum.StrEnum):
    """Enumeration of the different response codes from the scheduler."""

    SUCCESS = "success"
    NOT_IMPLEMENTED = "not_implemented"


class SchedulerError(TCodeResultReportInterface, Exception):
    """Custom exception for the scheduler."""

    success: bool = False

    def __init__(
        self, message: str, code: SchedulerCode, details: dict | None = None
    ) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}
        self.message = message


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


class ResolverResult(TCodeResultReportInterface):
    """Base class for results returned from the resolver submodule."""

    def __init__(
        self,
        success: bool,
        message: str | None = None,
        code: ResolverCode | None = None,
        details: dict | None = None,
    ) -> None:
        self.success = success
        self.message = message or ""
        self.code = code or ResolverCode.SUCCESS
        self.details = details or {}

    @classmethod
    def ok(cls, message: str | None = None, details: dict | None = None) -> Self:
        """Create a successful result."""
        return cls(True, message=message, details=details)

    @classmethod
    def error(
        cls, code: ResolverCode, message: str, details: dict | None = None
    ) -> Self:
        """Create a result containing an error. Enforces good exception practices through mandatory args."""
        return cls(False, code=code, message=message, details=details)
