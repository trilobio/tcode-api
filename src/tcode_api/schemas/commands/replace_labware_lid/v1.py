from typing import Literal

from ...common.docs import LabwareIdField, LidIdField
from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class REPLACE_LABWARE_LID(BaseRobotSpecificTCodeCommandV1):
    """Replace the lid on the target labware."""

    type: Literal["REPLACE_LABWARE_LID"] = "REPLACE_LABWARE_LID"
    schema_version: Literal[1] = 1

    labware_id: LabwareIdField
    lid_id: LidIdField
