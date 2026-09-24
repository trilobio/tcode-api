"""REPLACE_LABWARE_LID v2

- add offset_transform field
- add grasp_type field
"""

from typing import Literal

from pydantic import Field

from ....types import Matrix, identity_transform
from ...common.docs import LabwareIdField, LidIdField
from ...common.enums import GraspType
from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class REPLACE_LABWARE_LID(BaseRobotSpecificTCodeCommandV1):
    """Replace the lid on the target labware."""

    type: Literal["REPLACE_LABWARE_LID"] = "REPLACE_LABWARE_LID"
    schema_version: Literal[2] = 2

    labware_id: LabwareIdField
    lid_id: LidIdField

    offset_transform: Matrix = Field(
        default_factory=identity_transform,
        description="Optional offset transform applied during pickup.",
    )

    grasp_type: str = Field(
        default=GraspType.PINCH.value,
        description="Grasp type to use on the lid. Defaults to `GraspType.PINCH`.",
    )
