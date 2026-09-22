"""ASPIRATE v2

- Add optional relative_movement_offset parameter for moving aspiration.
"""

from typing import Literal

from pydantic import Field

from ....types import Matrix
from ...common.value_with_units import ValueWithUnits
from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class ASPIRATE(BaseRobotSpecificTCodeCommandV1):
    """Aspirate a given fluid volume at a given speed into the target robot's pipette."""

    type: Literal["ASPIRATE"] = "ASPIRATE"
    schema_version: Literal[2] = 2

    volume: ValueWithUnits = Field(description="Aspiration volume; expects volume units.")
    speed: ValueWithUnits = Field(description="Aspiration speed; expects volume/time units.")
    relative_movement_offset: Matrix | None = Field(
        default=None,
        description="Location in space to which to move relative to current location, in meters.",
    )
