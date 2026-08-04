from typing import Literal

from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class RETURN_PIPETTE_TIP_GROUP(BaseRobotSpecificTCodeCommandV1):
    """Return the currently held pipette tip group to its origin."""

    type: Literal["RETURN_PIPETTE_TIP_GROUP"] = "RETURN_PIPETTE_TIP_GROUP"
    schema_version: Literal[1] = 1
