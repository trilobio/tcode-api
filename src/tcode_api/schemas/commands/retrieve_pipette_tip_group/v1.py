from typing import Literal

from ...common.docs import PipetteTipGroupIdField
from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class RETRIEVE_PIPETTE_TIP_GROUP(BaseRobotSpecificTCodeCommandV1):
    """Pick up a pipette tip group using the held pipette."""

    type: Literal["RETRIEVE_PIPETTE_TIP_GROUP"] = "RETRIEVE_PIPETTE_TIP_GROUP"
    schema_version: Literal[1] = 1

    id: PipetteTipGroupIdField
