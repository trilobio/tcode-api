from typing import Literal

from ....base import BaseSchemaVersionedModel


class RoundBottomDescription(BaseSchemaVersionedModel):
    """Descriptor for a well with a spherical bottom.

    :note: The bottom of the well is assumed to be a hemisphere whose radius is inferred from the well's diameter.
    """

    type: Literal["Round"] = "Round"
    schema_version: Literal[1] = 1


class RoundBottomDescriptor(BaseSchemaVersionedModel):
    """:class:``RoundBottomDescription`` with optional parameters."""

    type: Literal["Round"] = "Round"
    schema_version: Literal[1] = 1
