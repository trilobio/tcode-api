"""TrashDescriptor & TrashDescription v3

- No changes; version bump only (Protocol Designer starts labware descriptors at v3).
"""

from typing import Literal

from pydantic import Field

from ...well.v1 import WellDescription, WellDescriptor
from ..base.labware_description.v1 import BaseLabwareDescriptionV1, BaseLabwareDescriptorV1

well_description = "Description of the waste volume as a well."


class TrashDescription(BaseLabwareDescriptionV1):
    """Description of a waste disposal container."""

    type: Literal["Trash"] = "Trash"
    schema_version: Literal[3] = 3

    well: WellDescription = Field(description=well_description)


class TrashDescriptor(BaseLabwareDescriptorV1):
    """:class:``TrashDescription`` with optional parameters."""

    type: Literal["Trash"] = "Trash"
    schema_version: Literal[3] = 3

    well: WellDescriptor | None = Field(description=well_description, default=None)
