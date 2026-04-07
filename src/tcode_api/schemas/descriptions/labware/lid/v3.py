# Protocol Designer starts the LabwareDescriptorBase at V3, so this increment has no changes.
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
