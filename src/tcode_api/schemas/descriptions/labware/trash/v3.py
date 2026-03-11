# Protocol Designer starts the LabwareDescriptorBase at V3, so this increment has no changes.
from typing import Literal

from pydantic import Field

from ...well.v1 import WellDescriptionV1, WellDescriptorV1
from ..base import BaseLabwareDescription, BaseLabwareDescriptor

well_description = "Description of the waste volume as a well."


class TrashDescriptionV3(BaseLabwareDescription):
    """Description of a waste disposal container."""

    type: Literal["Trash"] = "Trash"
    schema_version: Literal[3] = 3

    well: WellDescriptionV1 = Field(description=well_description)


class TrashDescriptorV3(BaseLabwareDescriptor):
    """:class:``TrashDescription`` with optional parameters."""

    type: Literal["Trash"] = "Trash"
    schema_version: Literal[3] = 3

    well: WellDescriptorV1 | None = Field(description=well_description, default=None)
