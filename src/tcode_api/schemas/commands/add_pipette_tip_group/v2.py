from typing import Literal

from pydantic import Field

from ...descriptions.pipette_tip_group.v1 import PipetteTipGroupDescriptor
from ..base import BaseRobotSpecificTCodeCommand


class ADD_PIPETTE_TIP_GROUP(BaseRobotSpecificTCodeCommand):
    """Find a matching group of pipette tips on the fleet and assign it the given id.

    The resolved pipette tip group is scoped to the robot identified by ``robot_id``.

    :raises ValidatorError: ``ValidatorErrorCode.ID_EXISTS`` if ``id`` is already registered to
        a pipette tip group.
    """

    type: Literal["ADD_PIPETTE_TIP_GROUP"] = "ADD_PIPETTE_TIP_GROUP"
    schema_version: Literal[2] = 2

    id: str = Field(
        description=(
            "Identifier to assign to the resolved pipette tip group. "
            "This id is used in subsequent commands to reference this pipette tip group."
        )
    )

    descriptor: PipetteTipGroupDescriptor = Field(
        description=("Minimal descriptor of the desired pipette tip group; resolved on the fleet.")
    )
