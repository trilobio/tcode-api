from typing import Literal

from ..base import BaseRobotSpecificTCodeCommand


class RETURN_PIPETTE_TIP_GROUP_V1(BaseRobotSpecificTCodeCommand):
    """Return the currently held pipette tip group to its origin."""

    type: Literal["RETURN_PIPETTE_TIP_GROUP"] = "RETURN_PIPETTE_TIP_GROUP"
    schema_version: Literal[1] = 1
