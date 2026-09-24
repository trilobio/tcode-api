from typing import Literal

from pydantic import Field

from ...descriptions.labware.union import LabwareDescription
from ...labware_holder.union import LabwareHolder
from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class CREATE_LABWARE(BaseRobotSpecificTCodeCommandV1):
    """Create a new physical labware on the targeted robot's deck."""

    type: Literal["CREATE_LABWARE"] = "CREATE_LABWARE"
    schema_version: Literal[1] = 1

    description: LabwareDescription = Field(
        description="Full description of the labware to create."
    )

    holder: LabwareHolder = Field(description="Holder in which to place the new labware.")
