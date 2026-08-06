"""LidDescriptor & LidDescription v2

- No changes; version bump only (Protocol Designer starts labware descriptors at v3).
"""

from typing import Literal

from ..base.labware_description.v1 import BaseLabwareDescriptionV1, BaseLabwareDescriptorV1
from .v1 import StackableField


class LidDescription(BaseLabwareDescriptionV1):
    """Description of a plate lid."""

    type: Literal["Lid"] = "Lid"
    schema_version: Literal[2] = 2

    stackable: StackableField


class LidDescriptor(BaseLabwareDescriptorV1):
    """LidDescription with optional parameters."""

    type: Literal["Lid"] = "Lid"
    schema_version: Literal[2] = 2

    stackable: StackableField | None = None
