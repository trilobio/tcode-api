from typing import Literal

from pydantic import Field

from ...well.v1 import WellDescription, WellDescriptor
from ..base import BaseLabwareDescription, BaseLabwareDescriptor

well_description = "Description of the waste volume as a well."


class TrashDescription(BaseLabwareDescription):
    """Description of a waste disposal container."""

    type: Literal["Trash"] = "Trash"
    schema_version: Literal[1] = 1

    well: WellDescription = Field(description=well_description)


class TrashDescriptor(BaseLabwareDescriptor):
    """:class:``TrashDescription`` with optional parameters."""

    type: Literal["Trash"] = "Trash"
    schema_version: Literal[1] = 1

    well: WellDescriptor | None = Field(description=well_description, default=None)
