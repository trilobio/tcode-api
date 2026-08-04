"""REMOVE_LABWARE_LID v2

- add offset_transform field
- add grasp_type field
"""

from typing import Literal

from pydantic import Field

from ....types import Matrix, identity_transform
from ...common.docs import LabwareIdField
from ...common.enums import GraspType
from ...labware_holder.union import LabwareHolder
from ..base import BaseRobotSpecificTCodeCommand


class REMOVE_LABWARE_LID(BaseRobotSpecificTCodeCommand):
    """Remove the lid from the target labware."""

    type: Literal["REMOVE_LABWARE_LID"] = "REMOVE_LABWARE_LID"
    schema_version: Literal[2] = 2

    labware_id: LabwareIdField

    storage_holder: LabwareHolder | None = Field(
        default=None,
        description="Optional holder at which to store the removed lid.",
    )

    offset_transform: Matrix = Field(
        default_factory=identity_transform,
        description="Optional offset transform applied during lid pickup.",
    )

    grasp_type: str = Field(
        default=GraspType.PINCH.value,
        description="Grasp type to use on the lid. Defaults to `GraspType.PINCH`.",
    )
