from typing import Annotated, Literal

from pydantic import Field

from ..base.labware_description.v1 import BaseLabwareDescriptionV1, BaseLabwareDescriptorV1

StackableField = Annotated[
    bool,
    Field(
        description="Whether the lid supports stacking an ANSI-SLAS-compliant labware on top of it.",
    ),
]


class LidDescription(BaseLabwareDescriptionV1):
    """Description of a plate lid."""

    type: Literal["Lid"] = "Lid"
    schema_version: Literal[1] = 1

    stackable: StackableField


class LidDescriptor(BaseLabwareDescriptorV1):
    """LidDescription with optional parameters."""

    type: Literal["Lid"] = "Lid"
    schema_version: Literal[1] = 1

    stackable: StackableField | None = None
