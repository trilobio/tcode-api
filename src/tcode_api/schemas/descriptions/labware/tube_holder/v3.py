"""TubeHolderDescriptor & TubeHolderDescription v3

- No changes; version bump only (Protocol Designer starts labware descriptors at v3).
"""

from typing import Literal

from pydantic import Field

from ...grid.v1 import GridDescription, GridDescriptor
from ...tube.v1 import TubeDescription, TubeDescriptor
from ..base.labware_description.v1 import BaseLabwareDescriptionV1, BaseLabwareDescriptorV1

grid_description = "Grid defining the layout of tube slots in the tube holder."
tube_description = "Description of a tube held by the tube holder. All tubes are assumed identical."


class TubeHolderDescription(BaseLabwareDescriptionV1):
    """Description of a tube holder."""

    type: Literal["TubeHolder"] = "TubeHolder"
    schema_version: Literal[3] = 3

    grid: GridDescription = Field(description=grid_description)
    tube: TubeDescription = Field(description=tube_description)


class TubeHolderDescriptor(BaseLabwareDescriptorV1):
    """:class:``TubeHolderDescription`` with optional parameters."""

    type: Literal["TubeHolder"] = "TubeHolder"
    schema_version: Literal[3] = 3

    grid: GridDescriptor | None = Field(description=grid_description, default=None)
    tube: TubeDescriptor | None = Field(description=tube_description, default=None)
