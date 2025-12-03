"""Data structures for defining various robot-related entities in TCode.

TCode entites are various objects that can be referenced in TCode commands:
    - Robots
    - Tools
    - Labware Holders
    - Labware

:note: labware are complex enough that they have their own sub-module: tcode_api.api.labware
"""

import enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from tcode_api.api.core import (
    ValueWithUnits,
    _ConfiguredBaseModel,
    _verify_positive_nonzero_int,
)
from tcode_api.types import NamedTags, Tags


class PipetteTipGroupDescriptor(_ConfiguredBaseModel):
    """Grid layout of pipette tips."""

    type: Literal["PipetteTipGroup"] = "PipetteTipGroup"

    row_count: Annotated[int, _verify_positive_nonzero_int]
    column_count: Annotated[int, _verify_positive_nonzero_int]
    pipette_tip_tags: Tags = Field(default_factory=list)
    pipette_tip_named_tags: NamedTags = Field(default_factory=dict)


# Tool schemas


class _ToolBaseDescriptor(_ConfiguredBaseModel):
    """Base schema shared by all tools in the TOOL discriminated union."""

    ...


class ProbeDescriptor(_ToolBaseDescriptor):
    type: Literal["Probe"] = "Probe"


class GripperDescriptor(_ToolBaseDescriptor):
    type: Literal["Gripper"] = "Gripper"


class _PipetteBaseDescriptor(_ToolBaseDescriptor):
    min_volume: ValueWithUnits | None = Field(default=None)
    max_volume: ValueWithUnits | None = Field(default=None)
    max_speed: ValueWithUnits | None = Field(default=None)


class SingleChannelPipetteDescriptor(_PipetteBaseDescriptor):
    type: Literal["SingleChannelPipette"] = "SingleChannelPipette"


class EightChannelPipetteDescriptor(_PipetteBaseDescriptor):
    type: Literal["EightChannelPipette"] = "EightChannelPipette"


# Define the Tool discriminated union
ToolDescriptor = Annotated[
    SingleChannelPipetteDescriptor
    | EightChannelPipetteDescriptor
    | ProbeDescriptor
    | GripperDescriptor,
    Field(discriminator="type"),
]

PipetteDescriptor = Annotated[
    SingleChannelPipetteDescriptor | EightChannelPipetteDescriptor,
    Field(discriminator="type"),
]


class LabwareHolderDescriptor(BaseModel):
    """Descriptor for an entity that can hold labware."""

    type: Literal["LabwareHolder"] = "LabwareHolder"


class ToolHolderDescriptor(BaseModel):
    """Descriptor for an entity that can hold tools."""

    type: Literal["ToolHolder"] = "ToolHolder"


class RobotDescriptor(BaseModel):
    """Descriptor for a robot in the fleet."""

    type: Literal["Robot"] = "Robot"
    serial_number: str | None = None
    tools: dict[str, ToolDescriptor] = Field(default_factory=dict)
    tool_holders: dict[str, ToolHolderDescriptor] = Field(default_factory=dict)
    labware_holders: dict[str, LabwareHolderDescriptor] = Field(default_factory=dict)


class PathType(int, enum.Enum):
    """Enumeration of robot path types.

    DIRECT: robot moves to the target location directly in jointspace.
    SAFE: robot moves to the target location via a safe path.
    SHORTCUT: robot uses DIRECT if it is close to the target, othserwise SAFE.
    """

    DIRECT = 1
    SAFE = 2
    SHORTCUT = 3


class GraspType(str, enum.Enum):
    """Enumeration of robot gripper grasp types.

    PINCH: robot actively pinches the labware from the sides.
    LIFT: robot passively lifts the labware from the bottom.
    """

    UNSPECIFIED = "UNSPECIFIED"
    LIFT = "LIFT"
    PINCH = "PINCH"


class GripperStateType(int, enum.Enum):
    """Enumeration of robot gripper states.

    OPEN: gripper is fully open.
    CLOSED: gripper is fully closed.
    WIDTH: gripper is set to a specific distance between the fingers.
    """

    OPEN = 1
    CLOSE = 2
    WIDTH = 3


class TrajectoryType(int, enum.Enum):
    """Enumeration of trajectory types.

    JOINT_SQUARE: robot moves in joint space with square motor profiles.
    JOINT_TRAPEZOIDAL: robot moves in joint space with trapezoidal motor profiles.
    LINEAR: robot moves in cartesian space with non-uniform motor profiles.
    """

    JOINT_SQUARE = 1
    JOINT_TRAPEZOIDAL = 2
