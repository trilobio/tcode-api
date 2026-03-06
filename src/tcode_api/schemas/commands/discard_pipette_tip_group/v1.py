from typing import Literal

from ..base import BaseRobotSpecificTCodeCommand


class DISCARD_PIPETTE_TIP_GROUP_V1(BaseRobotSpecificTCodeCommand):
    """Dispose of the currently held pipette tip group."""

    type: Literal["DISCARD_PIPETTE_TIP_GROUP"] = "DISCARD_PIPETTE_TIP_GROUP"
    schema_version: Literal[1] = 1
