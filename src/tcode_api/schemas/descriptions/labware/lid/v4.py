"""LidDescriptor & LidDescription v4

- Now inherits from `BaseLabwareDescriptionV2`/`BaseLabwareDescriptorV2`, adding the required
  (resp. optional) `pinchable` field.
"""

from typing import Literal

from ..base.labware_description.v2 import BaseLabwareDescriptionV2, BaseLabwareDescriptorV2
from .v1 import StackableField


class LidDescription(BaseLabwareDescriptionV2):
    """Description of a plate lid."""

    type: Literal["Lid"] = "Lid"
    schema_version: Literal[4] = 4

    stackable: StackableField


class LidDescriptor(BaseLabwareDescriptorV2):
    """LidDescription with optional parameters."""

    type: Literal["Lid"] = "Lid"
    schema_version: Literal[4] = 4

    stackable: StackableField | None = None
