from typing import Literal

from pydantic import Field

from ..base.labware_holder.v1 import BaseLabwareHolderV1


class LabwareId(BaseLabwareHolderV1):
    """LabwareHolder specifed by a TCode-assigned labware ID."""

    type: Literal["LabwareId"] = "LabwareId"
    schema_version: Literal[1] = 1

    id: str = Field(
        description=(
            "TCode ID of the labware to target, "
            "assigned previously by the :class:``ADD_LABWARE`` command."
        ),
    )
