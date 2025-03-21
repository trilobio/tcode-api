"""Pydantic BaseModel definitions of TCode API."""

from enum import Enum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field


class BaseModelStrict(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


# Define the ValueWithUnits schema
class ValueWithUnits(BaseModelStrict):
    type: Literal["ValueWithUnits"] = "ValueWithUnits"
    magnitude: float
    units: str

    def __hash__(self):
        return hash(self.magnitude) ^ hash(self.units)

    def __str__(self):
        return f"{self.magnitude} {self.units}"


class EnumWithDisplayName(Enum):
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


class LocationType(EnumWithDisplayName):
    """Enumeration of different methods for specifying a location.

    LABWARE_INDEX: tuple of (str, int); str corresponds to Labware.serial, int is index into labware's locations.
    NODE_ID: identifier of a node in a fleet's Transform Tree.
    MATRIX: transformation matrix relative to the fleet's root node.
    """

    LABWARE_INDEX = (1, "LabwareIndex")
    NODE_ID = (2, "NodeId")
    MATRIX = (3, "Matrix")


class Location(BaseModelStrict):
    """Location schema."""

    type: LocationType
    data: tuple[str, int] | str | Matrix


# Define constraint schemas
class Probe(BaseModelStrict):
    type: Literal["Probe"] = "Probe"


class PipetteCommon(BaseModelStrict):
    min_volume: ValueWithUnits | None = Field(default=None)
    max_volume: ValueWithUnits | None = Field(default=None)
    max_speed: ValueWithUnits | None = Field(default=None)


class SingleChannelPipette(PipetteCommon):
    type: Literal["SingleChannelPipette"] = "SingleChannelPipette"


class EightChannelPipette(PipetteCommon):
    type: Literal["EightChannelPipette"] = "EightChannelPipette"


# Define the Tool discriminated union
Tool = Annotated[
    SingleChannelPipette | EightChannelPipette | Probe,
    Field(discriminator="type"),
]


class PathType(EnumWithDisplayName):
    """Enumeration of robot path types.

    DIRECT: robot moves to the target location directly in jointspace.
    SAFE: robot moves to the target location via a safe path.
    SHORTCUT: robot uses DIRECT if it is close to the target, othserwise SAFE.
    """

    DIRECT = (1, "Direct")
    SAFE = (2, "Safe")
    SHORTCUT = (3, "Shortcut")


class TrajectoryType(EnumWithDisplayName):
    """Enumeration of trajectory types.

    JOINT_SQUARE: robot moves in joint space with square motor profiles.
    JOINT_TRAPEZOIDAL: robot moves in joint space with trapezoidal motor profiles.
    LINEAR: robot moves in cartesian space with non-uniform motor profiles.
    """

    JOINT_SQUARE = (1, "Square")
    JOINT_TRAPEZOIDAL = (2, "Trapezoidal")


class TCODEBase(BaseModelStrict):
    pass


class ASPIRATE(TCODEBase):
    type: Literal["ASPIRATE"] = "ASPIRATE"
    volume: ValueWithUnits
    speed: ValueWithUnits


class DISPENSE(TCODEBase):
    type: Literal["DISPENSE"] = "DISPENSE"
    volume: ValueWithUnits
    speed: ValueWithUnits


Axes = Literal["x", "y", "z", "xy", "xz", "yz", "xyz"]


class CALIBRATE_FTS_NOISE_FLOOR(TCODEBase):
    type: Literal["CALIBRATE_FTS_NOISE_FLOOR"] = "CALIBRATE_FTS_NOISE_FLOOR"
    axes: Axes
    snr: float


class DROP_TIP(TCODEBase):
    type: Literal["DROP_TIP"] = "DROP_TIP"
    location: Location


class DROP_TOOL(TCODEBase):
    type: Literal["DROP_TOOL"] = "DROP_TOOL"


class GET_TIP(TCODEBase):
    type: Literal["GET_TIP"] = "GET_TIP"
    location: Location


class GET_TOOL(TCODEBase):
    type: Literal["GET_TOOL"] = "GET_TOOL"
    tool: Tool


class GOTO(TCODEBase):
    type: Literal["GOTO"] = "GOTO"
    location: Location
    path_type: PathType
    trajectory_type: TrajectoryType
    location_offset: Matrix = Field(default_factory=identity_transform_factory)
    flange: Location | None = None
    flange_offset: Matrix = Field(default_factory=identity_transform_factory)


class PROBE(TCODEBase):
    type: Literal["PROBE"] = "PROBE"
    location: Location
    location_offset: Matrix = Field(default_factory=identity_transform_factory)
    flange: Location | None = None
    flange_offset: Matrix = Field(default_factory=identity_transform_factory)
    speed_fraction: float
    backoff_distance: ValueWithUnits


class RESET_FTS(TCODEBase):
    type: Literal["RESET_FTS"] = "RESET_FTS"


TCODE = Annotated[
    ASPIRATE
    | CALIBRATE_FTS_NOISE_FLOOR
    | DISPENSE
    | DROP_TIP
    | DROP_TOOL
    | GET_TIP
    | GET_TOOL
    | GOTO
    | PROBE
    | RESET_FTS,
    Field(discriminator="type"),
]


class _LabwareBase(BaseModel):
    id: str
    row_count: int
    column_count: int
    row_pitch: ValueWithUnits
    column_pitch: ValueWithUnits
    tags: list[str] = Field(default_factory=list)
    named_tags: dict[str, str] = Field(default_factory=dict)


class WellPlate(_LabwareBase):
    type: Literal["WellPlate"] = "WellPlate"


class PipetteTipRack(_LabwareBase):
    type: Literal["PipetteTipRack"] = "PipetteTipRack"
    full: bool


class Trash(_LabwareBase):
    type: Literal["Trash"] = "Trash"


LABWARE = Annotated[
    WellPlate | PipetteTipRack | Trash,
    Field(discriminator="type"),
]


class Robot(BaseModelStrict):
    tools: list[Tool] = Field(default_factory=list)


class Fleet(BaseModelStrict):
    robots: list[Robot] = Field(default_factory=list)
    labware: list[LABWARE] = Field(default_factory=list)


class Metadata(BaseModelStrict):
    """TCode script metadata."""

    name: str
    timestamp: str  # ISO 8601 timestamp string
    tcode_api_version: str
    description: str | None = Field(default=None)


class TCodeAST(BaseModel):
    """Structure of a TCode script as an abstract syntax tree."""

    metadata: Metadata
    fleet: Fleet
    tcode: list[TCODE] = Field(default_factory=list)
