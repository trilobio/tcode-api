from typing import Literal

from pydantic import Field

from ....types import Matrix, identity_transform
from ...labware_holder.union import LabwareHolder
from ..base import BaseRobotSpecificTCodeCommand


class PUT_DOWN_LABWARE_V1(BaseRobotSpecificTCodeCommand):
    """Put down the currently held labware."""

    type: Literal["PUT_DOWN_LABWARE"] = "PUT_DOWN_LABWARE"
    schema_version: Literal[1] = 1

    holder: LabwareHolder = Field(description="Holder in which to place the labware.")

    offset_transform: Matrix = Field(
        default_factory=identity_transform,
        description="Optional offset transform applied during placement.",
    )
