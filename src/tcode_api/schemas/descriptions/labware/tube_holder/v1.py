from typing import Literal

from pydantic import Field

from ...grid.v1 import GridDescription, GridDescriptor
from ...tube.v1 import TubeDescription, TubeDescriptor
from ..base import BaseLabwareDescription, BaseLabwareDescriptor

grid_description = "Grid defining the layout of tube slots in the tube holder."
tube_description = "Description of a tube held by the tube holder. All tubes are assumed identical."


class TubeHolderDescription(BaseLabwareDescription):
    """Description of a tube holder."""

    type: Literal["TubeHolder"] = "TubeHolder"
    schema_version: Literal[1] = 1

    grid: GridDescription = Field(description=grid_description)
    tube: TubeDescription = Field(description=tube_description)


class TubeHolderDescriptor(BaseLabwareDescriptor):
    """:class:``TubeHolderDescription`` with optional parameters."""

    type: Literal["TubeHolder"] = "TubeHolder"
    schema_version: Literal[1] = 1

    grid: GridDescriptor | None = Field(description=grid_description, default=None)
    tube: TubeDescriptor | None = Field(description=tube_description, default=None)
