from typing import Literal

from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class DISCARD_PIPETTE_TIP_GROUP(BaseRobotSpecificTCodeCommandV1):
    """Dispose of the currently held pipette tip group."""

    type: Literal["DISCARD_PIPETTE_TIP_GROUP"] = "DISCARD_PIPETTE_TIP_GROUP"
    schema_version: Literal[1] = 1
