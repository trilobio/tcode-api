from typing import Literal

from pydantic import Field

from ....types import Matrix, identity_transform
from ...common.docs import LabwareIdField
from ...common.enums import GraspType
from ..base import BaseRobotSpecificTCodeCommand


class PICK_UP_LABWARE_V1(BaseRobotSpecificTCodeCommand):
    """Pick up a labware with the robot's plate gripper."""

    type: Literal["PICK_UP_LABWARE"] = "PICK_UP_LABWARE"
    schema_version: Literal[1] = 1

    labware_id: LabwareIdField

    grasp_type: str = Field(
        default=GraspType.UNSPECIFIED.value,
        description="Optional grasp type to use.",
    )

    offset_transform: Matrix = Field(
        default_factory=identity_transform,
        description="Optional offset transform applied during pickup.",
    )
