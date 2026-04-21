# Protocol Designer starts the LabwareDescriptorBase at V3, so this increment has no changes.
from typing import Literal

from pydantic import Field

from ....pipette_tip_layout.v1 import PipetteTipLayout
from ...grid.v1 import GridDescription, GridDescriptor
from ...pipette_tip.v1 import PipetteTipDescription, PipetteTipDescriptor
from ..base import BaseLabwareDescription, BaseLabwareDescriptor

grid_description = "Layout of the pipette tip box slots. typically an 8*12 grid for a 96 tip box."

pipette_tip_description = (
    "Description of the pipette tips used in the box. All pipette tips are assumed to be identical."
)
pipette_tip_layout_description = (
    "Specifies which slots contain pipette tips."
    "If not provided, it is assumed that all slots in the grid are filled with pipette tips."
)


class PipetteTipBoxDescription(BaseLabwareDescription):
    """Description of a pipette tip box."""

    type: Literal["PipetteTipBox"] = "PipetteTipBox"
    schema_version: Literal[3] = 3

    grid: GridDescription = Field(
        description=grid_description,
    )
    pipette_tip: PipetteTipDescription = Field(
        description=pipette_tip_description,
    )
    pipette_tip_layout: PipetteTipLayout = Field(
        default_factory=PipetteTipLayout.full,
        description=pipette_tip_layout_description,
    )


class PipetteTipBoxDescriptor(BaseLabwareDescriptor):
    """PipetteTipBoxDescription with optional parameters."""

    type: Literal["PipetteTipBox"] = "PipetteTipBox"
    schema_version: Literal[3] = 3

    grid: GridDescriptor | None = Field(
        default=None,
        description=grid_description,
    )
    pipette_tip: PipetteTipDescriptor | None = Field(
        default=None,
        description=pipette_tip_description,
    )
    pipette_tip_layout: PipetteTipLayout | None = Field(
        default=None,
        description=pipette_tip_layout_description,
    )
