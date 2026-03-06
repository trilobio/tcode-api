from typing import Literal

from ...common.docs import LabwareIdField, LidIdField
from ..base import BaseRobotSpecificTCodeCommand


class REPLACE_LABWARE_LID_V1(BaseRobotSpecificTCodeCommand):
    """Replace the lid on the target labware."""

    type: Literal["REPLACE_LABWARE_LID"] = "REPLACE_LABWARE_LID"
    schema_version: Literal[1] = 1

    labware_id: LabwareIdField
    lid_id: LidIdField
