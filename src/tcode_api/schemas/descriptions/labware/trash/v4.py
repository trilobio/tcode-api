"""TrashDescriptor & TrashDescription v4

- Now inherits from `BaseLabwareDescriptionV2`/`BaseLabwareDescriptorV2`, adding the required
  (resp. optional) `pinchable` field.
"""

from typing import Literal

from pydantic import Field

from ...well.v1 import WellDescription, WellDescriptor
from ..base.labware_description.v2 import BaseLabwareDescriptionV2, BaseLabwareDescriptorV2

well_description = "Description of the waste volume as a well."


class TrashDescription(BaseLabwareDescriptionV2):
    """Description of a waste disposal container."""

    type: Literal["Trash"] = "Trash"
    schema_version: Literal[4] = 4

    well: WellDescription = Field(description=well_description)


class TrashDescriptor(BaseLabwareDescriptorV2):
    """:class:``TrashDescription`` with optional parameters."""

    type: Literal["Trash"] = "Trash"
    schema_version: Literal[4] = 4

    well: WellDescriptor | None = Field(description=well_description, default=None)
