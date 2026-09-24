from typing import Literal

from pydantic import Field

from ...common.value_with_units import ValueWithUnits
from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class WAIT(BaseRobotSpecificTCodeCommandV1):
    """Delay execution for a specified duration."""

    type: Literal["WAIT"] = "WAIT"
    schema_version: Literal[1] = 1

    duration: ValueWithUnits = Field(description="Duration to wait; expects time units.")
