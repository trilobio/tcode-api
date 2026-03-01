from typing import Literal

from pydantic import Field

from ...common.docs import LabwareIdField
from ...labware_holder.union import LabwareHolder
from ..base import BaseRobotSpecificTCodeCommand


class REMOVE_LABWARE_LID_V1(BaseRobotSpecificTCodeCommand):
    """Remove the lid from the target labware."""

    type: Literal["REMOVE_LABWARE_LID"] = "REMOVE_LABWARE_LID"
    schema_version: Literal[1] = 1

    labware_id: LabwareIdField

    storage_holder: LabwareHolder | None = Field(
        default=None,
        description="Optional holder at which to store the removed lid.",
    )
