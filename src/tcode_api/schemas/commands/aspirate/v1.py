from typing import Literal

from pydantic import Field

from ...common.value_with_units import ValueWithUnits
from ..base import BaseRobotSpecificTCodeCommand


class ASPIRATE_V1(BaseRobotSpecificTCodeCommand):
    """Aspirate a given fluid volume at a given speed into the target robot's pipette."""

    type: Literal["ASPIRATE"] = "ASPIRATE"
    schema_version: Literal[1] = 1

    volume: ValueWithUnits = Field(description="Aspiration volume; expects volume units.")
    speed: ValueWithUnits = Field(description="Aspiration speed; expects volume/time units.")
