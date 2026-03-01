from typing import Literal

from pydantic import Field

from ...grid.v1 import GridDescriptionV1, GridDescriptorV1
from ...tube.v1 import TubeDescriptionV1, TubeDescriptorV1
from ..base import BaseLabwareDescription, BaseLabwareDescriptor

grid_description = "Grid defining the layout of tube slots in the tube holder."
tube_description = "Description of a tube held by the tube holder. All tubes are assumed identical."


class TubeHolderDescriptionV1(BaseLabwareDescription):
    """Description of a tube holder."""

    type: Literal["TubeHolder"] = "TubeHolder"
    schema_version: Literal[1] = 1

    grid: GridDescriptionV1 = Field(description=grid_description)
    tube: TubeDescriptionV1 = Field(description=tube_description)


class TubeHolderDescriptorV1(BaseLabwareDescriptor):
    """:class:``TubeHolderDescription`` with optional parameters."""

    type: Literal["TubeHolder"] = "TubeHolder"
    schema_version: Literal[1] = 1

    grid: GridDescriptorV1 | None = Field(description=grid_description, default=None)
    tube: TubeDescriptorV1 | None = Field(description=tube_description, default=None)
