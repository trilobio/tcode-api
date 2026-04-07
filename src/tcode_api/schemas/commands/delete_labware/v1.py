from typing import Literal

from ...common.docs import LabwareIdField
from ..base import BaseRobotSpecificTCodeCommand


class DELETE_LABWARE(BaseRobotSpecificTCodeCommand):
    """Physically remove a labware from the robot's deck."""

    type: Literal["DELETE_LABWARE"] = "DELETE_LABWARE"
    schema_version: Literal[1] = 1

    labware_id: LabwareIdField
