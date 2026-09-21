"""ADD_PIPETTE_TIP_GROUP v3

- Make descriptor able to take None
- Add pipette_tip_locations field to allow specifying a group of tips by location instead of descriptor
"""

from typing import Literal

from pydantic import Field

from ...descriptions.pipette_tip_group.v1 import PipetteTipGroupDescriptor
from ...location.location_as_labware_index.v1 import LocationAsLabwareIndex
from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class ADD_PIPETTE_TIP_GROUP(BaseRobotSpecificTCodeCommandV1):
    """Find a matching group of pipette tips on the fleet and assign it the given id.

    The resolved pipette tip group is scoped to the robot identified by ``robot_id``.

    :raises ValidatorError: ``ValidatorErrorCode.ID_EXISTS`` if ``id`` is already registered to
        a pipette tip group.
    :raises ValidatorError: ``ValidatorErrorCode.INVALID_PIPETTE_TIP_GROUP_SHAPE`` if no matching
        pipette tip group can be found.
    :raises ValidatorError: ``ValidatorErrorCode.INVALID_EITHER_OR_PARAMETERS`` if both or neither
        of ``descriptor`` and ``pipette_tip_locations`` are provided.
    """

    type: Literal["ADD_PIPETTE_TIP_GROUP"] = "ADD_PIPETTE_TIP_GROUP"
    schema_version: Literal[3] = 3

    id: str = Field(
        description=(
            "Identifier to assign to the resolved pipette tip group. "
            "This id is used in subsequent commands to reference this pipette tip group."
        )
    )

    descriptor: PipetteTipGroupDescriptor | None = Field(
        description=(
            "Minimal descriptor of the desired pipette tip group; resolved on the fleet, or None "
            "if `pipette_tip_locations` is provided instead."
        ),
        default=None,
    )
    pipette_tip_locations: list[LocationAsLabwareIndex] | None = Field(
        description=(
            "Locations of tips making up the desired pipette tip group, or None if `descriptor` is "
            "provided instead."
        ),
        default=None,
    )
