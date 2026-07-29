"""LidDescriptor & LidDescription v3

- No changes; version bump only (Protocol Designer starts labware descriptors at v3).
"""

from typing import Literal

from ..base import BaseLabwareDescription, BaseLabwareDescriptor
from .v1 import StackableField


class LidDescription(BaseLabwareDescription):
    """Description of a plate lid."""

    type: Literal["Lid"] = "Lid"
    schema_version: Literal[3] = 3

    stackable: StackableField


class LidDescriptor(BaseLabwareDescriptor):
    """LidDescription with optional parameters."""

    type: Literal["Lid"] = "Lid"
    schema_version: Literal[3] = 3

    stackable: StackableField | None = None
