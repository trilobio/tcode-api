from typing import Literal

from ...common.docs import PipetteTipGroupIdField
from ..base import BaseRobotSpecificTCodeCommand


class RETRIEVE_PIPETTE_TIP_GROUP_V1(BaseRobotSpecificTCodeCommand):
    """Pick up a pipette tip group using the held pipette."""

    type: Literal["RETRIEVE_PIPETTE_TIP_GROUP"] = "RETRIEVE_PIPETTE_TIP_GROUP"
    schema_version: Literal[1] = 1

    id: PipetteTipGroupIdField
