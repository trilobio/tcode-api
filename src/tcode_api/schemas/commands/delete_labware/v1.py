from typing import Literal

from ...common.docs import LabwareIdField
from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class DELETE_LABWARE(BaseRobotSpecificTCodeCommandV1):
    """Physically remove a labware from the robot's deck."""

    type: Literal["DELETE_LABWARE"] = "DELETE_LABWARE"
    schema_version: Literal[1] = 1

    labware_id: LabwareIdField
