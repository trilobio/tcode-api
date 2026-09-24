from typing import Literal

from pydantic import Field

from ...location.union import Location
from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class PUT_DOWN_PIPETTE_TIP(BaseRobotSpecificTCodeCommandV1):
    """Put down the currently held pipette tip(s)."""

    type: Literal["PUT_DOWN_PIPETTE_TIP"] = "PUT_DOWN_PIPETTE_TIP"
    schema_version: Literal[1] = 1

    location: Location = Field(description="Location at which to put down the pipette tip(s).")
