"""Pydantic BaseModel definitions of TCode API."""
from __future__ import annotations

from enum import Enum
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class TCODEBase(BaseModelStrict):
    pass


class EnumWithDisplayName(Enum):
    """Base class for Enum with display_name attribute."""

    def __init__(self, value: int, display_name: str):
        self._value_ = value
        self.display_name = display_name

    @classmethod
    def from_value(cls, value: str | int) -> EnumWithDisplayName:
        match type(value):
            # Attempt to match by value
            case int():
                for member in cls:
                    if member.value == value:
                        return member

            # Attempt to match by name or display_name
            case str():
                for member in cls:
                    if member.name == value.upper() or member.display_name == value:
                        return member

            case _:
                raise TypeError(f"Invalid value type: {type(value)}")


Matrix = list[list[float]]


class Location(BaseModelStrict):
    """Resolvable location on a robot.

    Three options:
    - (int): 0-based index into a Fleet's labware list
    - (str): name of a node in a robot's TransformTree
    - (Matrix): transformation matrix relative to the robot's base
    """
    data: Union[int, str, Matrix]


# Define constraint schemas
class Probe(BaseModelStrict):
    type: Literal["Probe"] = "Probe"


class PipetteCommon(BaseModelStrict):
    min_volume: Optional[ValueWithUnits] = Field(default=None)
    max_volume: Optional[ValueWithUnits] = Field(default=None)
    max_speed: Optional[ValueWithUnits] = Field(default=None)


class Gripper(BaseModelStrict):
    type: Literal["Gripper"] = "Gripper"
    motor_position_open: float
    motor_position_closed: float


class SingleChannelPipette(PipetteCommon):
    type: Literal["SingleChannelPipette"] = "SingleChannelPipette"


class EightChannelPipette(PipetteCommon):
    type: Literal["EightChannelPipette"] = "EightChannelPipette"


# Define the Tool discriminated union
Tool = Annotated[
    Union[SingleChannelPipette, EightChannelPipette, Probe, Gripper],
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


class ASPIRATE(TCODEBase):
    type: Literal["ASPIRATE"] = "ASPIRATE"
    volume: ValueWithUnits
    speed: ValueWithUnits


class DISPENSE(TCODEBase):
    type: Literal["DISPENSE"] = "DISPENSE"
    volume: ValueWithUnits
    speed: ValueWithUnits


class CALIBRATE_FTS_NOISE_FLOOR(TCODEBase):
    type: Literal["CALIBRATE_FTS_NOISE_FLOOR"] = "CALIBRATE_FTS_NOISE_FLOOR"
    axes: str
    snr: float


class DROP_LABWARE(TCODEBase):
    type: Literal["DROP_LABWARE"] = "DROP_LABWARE"
    location: Location


class DROP_TIP(TCODEBase):
    type: Literal["DROP_TIP"] = "DROP_TIP"
    location: Location


class DROP_TOOL(TCODEBase):
    type: Literal["DROP_TOOL"] = "DROP_TOOL"


class GET_LABWARE(TCODEBase):
    type: Literal["GET_LABWARE"] = "GET_LABWARE"
    location: Location


class GET_TIP(TCODEBase):
    type: Literal["GET_TIP"] = "GET_TIP"
    location: Location


class GET_TOOL(TCODEBase):
    type: Literal["GET_TOOL"] = "GET_TOOL"
    tool: Tool


class GOTO(TCODEBase):
    type: Literal["GOTO"] = "GOTO"
    location: Location
    location_offset: Matrix
    flange: Location
    flange_offset: Matrix
    path_type: PathType
    trajectory_type: TrajectoryType


class PROBE(TCODEBase):
    type: Literal["PROBE"] = "PROBE"
    location: Location
    location_offset: Matrix
    flange: Location
    flange_offset: Matrix
    speed_fraction: float
    backoff_distance: ValueWithUnits


class RESET_FTS(TCODEBase):
    type: Literal["RESET_FTS"] = "RESET_FTS"


TCODE = Annotated[
    Union[
        ASPIRATE,
        CALIBRATE_FTS_NOISE_FLOOR,
        DISPENSE,
        DROP_LABWARE,
        DROP_TIP,
        DROP_TOOL,
        GET_LABWARE,
        GET_TIP,
        GET_TOOL,
        GOTO,
        PROBE,
        RESET_FTS,
    ],
    Field(discriminator="type"),
]


class LabwareType(EnumWithDisplayName):
    SAMPLE = (1, "Sample")
    TIP = (2, "Tip")
    TRASH = (3, "Trash")


class Labware(BaseModel):
    rows: int
    columns: int
    type: Optional[LabwareType] = Field(default=None)
    serial: Optional[str] = Field(default=None)

    @field_validator("type", mode="before")
    def parse_type(cls, v):
        if v is None:
            return v
        if isinstance(v, LabwareType):
            return v
        try:
            return LabwareType.from_value(v)
        except ValueError as e:
            raise ValueError(f"Invalid LabwareType: {v}") from e


class Robot(BaseModelStrict):
    tools: list[Tool] = Field(default_factory=list)


class Fleet(BaseModelStrict):
    robots: list[Robot] = Field(default_factory=list)
    labware: list[Labware] = Field(default_factory=list)


class TCodeAST(BaseModel):
    """Structure of a TCode script as an abstract syntax tree."""

    fleet: Fleet
    tcode: List[TCODE] = Field(default_factory=list)
