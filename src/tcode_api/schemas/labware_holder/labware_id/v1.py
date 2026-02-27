from typing import Literal

from pydantic import Field

from ..base import BaseLabwareHolder


class LabwareIdV1(BaseLabwareHolder):
    """LabwareHolder specifed by a TCode-assigned labware ID."""

    type: Literal["LabwareId"] = "LabwareId"
    schema_version: Literal[1] = 1

    id: str = Field(
        description=(
            "TCode ID of the labware to target, "
            "assigned previously by the :class:``ADD_LABWARE`` command."
        ),
    )
