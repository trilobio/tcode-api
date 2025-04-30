"""Pydantic BaseModel definitions of TCode API."""

from enum import Enum
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field


class _BaseModelStrict(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


class _BaseModelWithId(_BaseModelStrict):
    id: str


# Define the ValueWithUnits schema
class ValueWithUnits(_BaseModelStrict):
    type: Literal["ValueWithUnits"] = "ValueWithUnits"
    magnitude: float
    units: str

    def __hash__(self):
        # TODO (connor): Mia mentioned that this can produce collisions, fix.
        return hash(self.magnitude) ^ hash(self.units)

    def __str__(self):
        return f"{self.magnitude} {self.units}"


class _EnumWithDisplayName(Enum):
    """Base class for Enum with display_name attribute."""

    def __init__(self, value: int, display_name: str):
        self._value_ = value
        self.display_name = display_name

    @classmethod
    def from_value(cls, value: str | int) -> Self:
        if isinstance(value, int):
            for member in cls:
                if member.value == value:
                    return member

        elif isinstance(value, str):
            for member in cls:
                if member.name == value.upper() or member.display_name == value:
                    return member

        else:
            raise TypeError(f"Invalid value type: {type(value)}")

        raise ValueError("Invalid value: {value}")


Matrix = list[list[float]]


def identity_transform_factory() -> Matrix:
    """Create new list of lists representing an identity matrix."""
    return [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def verify_positive_nonzero_int(value: int) -> int:
    """Validator to ensure the value is a positive non-zero integer."""
    if value <= 0:
        raise ValueError(f"Value must be > 0, not {value}")

    return value


class _Location(_BaseModelStrict):
    """Base schema shared by all locations in the Location discriminated union."""

    type: str


class LocationAsNodeId(_Location):
    """Location specified by a node ID in the fleet's transform tree."""

    type: Literal["NodeId"] = "NodeId"
    data: str


class LocationAsLabwareIndex(_Location):
    """Location specified by a tuple of labware id and labware location index."""

    type: Literal["LabwareIndex"] = "LabwareIndex"
    data: tuple[str, int] | Any  # (labware_id, location_index)


class LocationAsMatrix(_Location):
    """Location specified by a transformation matrix relative to the fleet's root node."""

    type: Literal["Matrix"] = "Matrix"
    data: Matrix  # 4x4 transformation matrix


Location = Annotated[
    LocationAsNodeId | LocationAsLabwareIndex | LocationAsMatrix,
    Field(discriminator="type"),
]


class PipetteTipGroup(_BaseModelWithId):
    """Grid layout of pipette tips."""

    row_count: Annotated[int, verify_positive_nonzero_int]
    column_count: Annotated[int, verify_positive_nonzero_int]
    pipette_tip_tags: list[str] = Field(default_factory=list)
    pipette_tip_named_tags: dict[str, str] = Field(default_factory=dict)


# Tool schemas


class _ToolBase(_BaseModelWithId):
    """Base schema shared by all tools in the TOOL discriminated union."""

    ...


class Probe(_ToolBase):
    type: Literal["Probe"] = "Probe"


class Gripper(_ToolBase):
    type: Literal["Gripper"] = "Gripper"


class _PipetteCommon(_ToolBase):
    min_volume: ValueWithUnits | None = Field(default=None)
    max_volume: ValueWithUnits | None = Field(default=None)
    max_speed: ValueWithUnits | None = Field(default=None)


class SingleChannelPipette(_PipetteCommon):
    type: Literal["SingleChannelPipette"] = "SingleChannelPipette"


class EightChannelPipette(_PipetteCommon):
    type: Literal["EightChannelPipette"] = "EightChannelPipette"


# Define the Tool discriminated union
Tool = Annotated[
    EightChannelPipette | Gripper | Probe | SingleChannelPipette,
    Field(discriminator="type"),
]


class PathType(int, Enum):
    """Enumeration of robot path types.

    DIRECT: robot moves to the target location directly in jointspace.
    SAFE: robot moves to the target location via a safe path.
    SHORTCUT: robot uses DIRECT if it is close to the target, othserwise SAFE.
    """

    DIRECT = 1
    SAFE = 2
    SHORTCUT = 3


class TrajectoryType(int, Enum):
    """Enumeration of trajectory types.

    JOINT_SQUARE: robot moves in joint space with square motor profiles.
    JOINT_TRAPEZOIDAL: robot moves in joint space with trapezoidal motor profiles.
    LINEAR: robot moves in cartesian space with non-uniform motor profiles.
    """

    JOINT_SQUARE = 1
    JOINT_TRAPEZOIDAL = 2


# TCode command schemas


class _TCodeBase(_BaseModelStrict):
    """Base schema shared by all TCode commands in the TCODE discriminated union."""

    ...


class ASPIRATE(_TCodeBase):
    type: Literal["ASPIRATE"] = "ASPIRATE"
    volume: ValueWithUnits
    speed: ValueWithUnits


Axes = Literal["x", "y", "z", "xy", "xz", "yz", "xyz"]


class CALIBRATE_FTS_NOISE_FLOOR(_TCodeBase):
    type: Literal["CALIBRATE_FTS_NOISE_FLOOR"] = "CALIBRATE_FTS_NOISE_FLOOR"
    axes: Axes
    snr: float


class COMMENTS(_TCodeBase):
    type: Literal["COMMENTS"] = "COMMENTS"
    text: str


class DISCARD_PIPETTE_TIP_GROUP(_TCodeBase):
    type: Literal["DISCARD_PIPETTE_TIP_GROUP"] = "DISCARD_PIPETTE_TIP_GROUP"


class DISPENSE(_TCodeBase):
    type: Literal["DISPENSE"] = "DISPENSE"
    volume: ValueWithUnits
    speed: ValueWithUnits


class GOTO(_TCodeBase):
    type: Literal["GOTO"] = "GOTO"
    location: Location
    location_offset: Matrix = Field(default_factory=identity_transform_factory)
    flange: Location | None = None
    flange_offset: Matrix = Field(default_factory=identity_transform_factory)
    path_type: int | None = None  # PathType | None = None
    trajectory_type: int | None = None  # TrajectoryType | None = None


class PAUSE(_TCodeBase):
    type: Literal["PAUSE"] = "PAUSE"


class REMOVE_PLATE_LID(_TCodeBase):
    type: Literal["REMOVE_PLATE_LID"] = "REMOVE_PLATE_LID"
    plate_id: str
    storage_location: Location | None = None


class REPLACE_PLATE_LID(_TCodeBase):
    type: Literal["REPLACE_PLATE_LID"] = "REPLACE_PLATE_LID"
    plate_id: str
    lid_id: str | None = None


class PICK_UP_PIPETTE_TIP(_TCodeBase):
    type: Literal["PICK_UP_PIPETTE_TIP"] = "PICK_UP_PIPETTE_TIP"
    location: Location


class PICK_UP_TOOL(_TCodeBase):
    type: Literal["PICK_UP_TOOL"] = "PICK_UP_TOOL"
    location: Location


class PROBE(_TCodeBase):
    type: Literal["PROBE"] = "PROBE"
    location: Location
    location_offset: Matrix = Field(default_factory=identity_transform_factory)
    flange: Location | None = None
    flange_offset: Matrix = Field(default_factory=identity_transform_factory)
    speed_fraction: float
    backoff_distance: ValueWithUnits


class PUT_DOWN_PIPETTE_TIP(_TCodeBase):
    type: Literal["PUT_DOWN_PIPETTE_TIP"] = "PUT_DOWN_PIPETTE_TIP"
    location: Location


class PUT_DOWN_TOOL(_TCodeBase):
    type: Literal["PUT_DOWN_TOOL"] = "PUT_DOWN_TOOL"
    location: Location


class RESET_FTS(_TCodeBase):
    type: Literal["RESET_FTS"] = "RESET_FTS"


class RETRIEVE_PIPETTE_TIP_GROUP(_TCodeBase):
    type: Literal["RETRIEVE_PIPETTE_TIP_GROUP"] = "RETRIEVE_PIPETTE_TIP_GROUP"
    id: str


class RETRIEVE_TOOL(_TCodeBase):
    type: Literal["RETRIEVE_TOOL"] = "RETRIEVE_TOOL"
    id: str


class RETURN_PIPETTE_TIP_GROUP(_TCodeBase):
    type: Literal["RETURN_PIPETTE_TIP_GROUP"] = "RETURN_PIPETTE_TIP_GROUP"


class RETURN_TOOL(_TCodeBase):
    type: Literal["RETURN_TOOL"] = "RETURN_TOOL"


TCode = Annotated[
    ASPIRATE
    | CALIBRATE_FTS_NOISE_FLOOR
    | COMMENTS
    | DISCARD_PIPETTE_TIP_GROUP
    | DISPENSE
    | GOTO
    | PAUSE
    | PICK_UP_PIPETTE_TIP
    | PICK_UP_TOOL
    | PROBE
    | PUT_DOWN_PIPETTE_TIP
    | PUT_DOWN_TOOL
    | REMOVE_PLATE_LID
    | REPLACE_PLATE_LID
    | RESET_FTS
    | RETRIEVE_PIPETTE_TIP_GROUP
    | RETRIEVE_TOOL
    | RETURN_PIPETTE_TIP_GROUP
    | RETURN_TOOL,
    Field(discriminator="type"),
]


# Various plate schemas #
# Note: called Labware for historical reasons, but all correspond to the ANSI-SLAS format


class _LabwareBase(_BaseModelWithId):
    """Base schema shared by all labware in the Labware discriminated union."""

    row_count: int
    column_count: int
    row_pitch: ValueWithUnits
    column_pitch: ValueWithUnits
    has_lid: bool
    tags: list[str] = Field(default_factory=list)
    named_tags: dict[str, str] = Field(default_factory=dict)


class WellPlate(_LabwareBase):
    type: Literal["WellPlate"] = "WellPlate"


class PipetteTipRack(_LabwareBase):
    type: Literal["PipetteTipRack"] = "PipetteTipRack"
    full: bool = True


class Trash(_LabwareBase):
    type: Literal["Trash"] = "Trash"


class Lid(_LabwareBase):
    type: Literal["Lid"] = "Lid"


Labware = Annotated[
    WellPlate | PipetteTipRack | Trash | Lid,
    Field(discriminator="type"),
]


# Top-level component schemas


class Robot(_BaseModelWithId):
    tools: list[Tool] = Field(default_factory=list)


class Fleet(_BaseModelStrict):
    robots: list[Robot] = Field(default_factory=list)
    labware: list[Labware] = Field(default_factory=list)


class Metadata(_BaseModelStrict):
    """TCode script metadata."""

    name: str
    timestamp: str  # ISO 8601 timestamp string
    tcode_api_version: str
    description: str | None = Field(default=None)


class TCodeAST(BaseModel):
    """Structure of a TCode script as an abstract syntax tree."""

    metadata: Metadata
    fleet: Fleet
    tcode: list[TCode] = Field(default_factory=list)
    pipette_tips: list[PipetteTipGroup] = Field(default_factory=list)
