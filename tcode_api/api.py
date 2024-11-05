"""Pydantic BaseModel definitions of TCode API."""
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


# Define constraint schemas
class PipetteCommon(BaseModelStrict):
    min_volume: Optional[ValueWithUnits] = Field(default=None)
    max_volume: Optional[ValueWithUnits] = Field(default=None)
    max_speed: Optional[ValueWithUnits] = Field(default=None)


class SingleChannelPipette(PipetteCommon):
    type: Literal["SingleChannelPipette"] = "SingleChannelPipette"


class EightChannelPipette(PipetteCommon):
    type: Literal["EightChannelPipette"] = "EightChannelPipette"


# Define the Tool discriminated union
Tool = Annotated[
    Union[SingleChannelPipette, EightChannelPipette],
    Field(discriminator="type"),
]


class GET_TOOL(TCODEBase):
    type: Literal["GET_TOOL"] = "GET_TOOL"
    tool: Tool

class DROP_TOOL(TCODEBase):
    type: Literal["DROP_TOOL"] = "DROP_TOOL"


class GET_TIP(TCODEBase):
    type: Literal["GET_TIP"] = "GET_TIP"
    location: int


Matrix = list[list[float]]


class GOTO(TCODEBase):
    type: Literal["GOTO"] = "GOTO"
    location: int
    location_offset: Matrix
    tool_offset: Matrix


class ASPIRATE(TCODEBase):
    type: Literal["ASPIRATE"] = "ASPIRATE"
    volume: ValueWithUnits
    speed: ValueWithUnits


class DISPENSE(TCODEBase):
    type: Literal["DISPENSE"] = "DISPENSE"
    volume: ValueWithUnits
    speed: ValueWithUnits


class DROP_TIP(TCODEBase):
    type: Literal["DROP_TIP"] = "DROP_TIP"
    location: int


TCODE = Annotated[
    Union[GET_TOOL, GET_TIP, GOTO, ASPIRATE, DISPENSE, DROP_TIP, DROP_TOOL],
    Field(discriminator="type"),
]


class LabwareType(Enum):
    SAMPLE = (1, "Sample")
    TIP = (2, "Tip")
    TRASH = (3, "Trash")

    def __init__(self, value, display_name):
        self._value_ = value
        self.display_name = display_name

    @classmethod
    def from_value(cls, value):
        # Attempt to match by value
        if isinstance(value, int):
            for member in cls:
                if member.value == value:
                    return member
        # Attempt to match by name or display_name
        if isinstance(value, str):
            for member in cls:
                if member.name == value.upper() or member.display_name == value:
                    return member
        raise ValueError(f"'{value}' is not a valid LabwareType")


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
