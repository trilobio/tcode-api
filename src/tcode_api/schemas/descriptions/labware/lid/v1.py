from typing import Annotated, Literal

from pydantic import Field

from ..base import BaseLabwareDescription, BaseLabwareDescriptor

StackableField = Annotated[
    bool,
    Field(
        description="Whether the lid supports stacking an ANSI-SLAS-compliant labware on top of it.",
    ),
]


class LidDescriptionV1(BaseLabwareDescription):
    """Description of a plate lid."""

    type: Literal["Lid"] = "Lid"
    schema_version: Literal[1] = 1

    stackable: StackableField


class LidDescriptorV1(BaseLabwareDescriptor):
    """LidDescription with optional parameters."""

    type: Literal["Lid"] = "Lid"
    schema_version: Literal[1] = 1

    stackable: StackableField | None = None
