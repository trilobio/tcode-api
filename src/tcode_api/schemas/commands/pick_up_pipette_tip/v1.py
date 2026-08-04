from typing import Literal

from pydantic import Field

from ...location.union import Location
from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class PICK_UP_PIPETTE_TIP(BaseRobotSpecificTCodeCommandV1):
    """Pick up pipette tip(s) at the specified location."""

    type: Literal["PICK_UP_PIPETTE_TIP"] = "PICK_UP_PIPETTE_TIP"
    schema_version: Literal[1] = 1

    location: Location = Field(description="Location at which to pick up the pipette tip(s).")
