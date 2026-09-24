from typing import Literal

from pydantic import Field

from ...common.value_with_units import ValueWithUnits
from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class DISPENSE(BaseRobotSpecificTCodeCommandV1):
    """Dispense a given fluid volume at a given speed."""

    type: Literal["DISPENSE"] = "DISPENSE"
    schema_version: Literal[1] = 1

    volume: ValueWithUnits = Field(description="Dispense volume; expects volume units.")

    speed: ValueWithUnits = Field(description="Dispense speed; expects volume/time units.")
