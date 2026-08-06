from typing import Literal

from ....base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1


class RoundBottomDescription(BaseSchemaVersionedModelV1):
    """Descriptor for a well with a spherical bottom.

    :note: The bottom of the well is assumed to be a hemisphere whose radius is inferred from the well's diameter.
    """

    type: Literal["Round"] = "Round"
    schema_version: Literal[1] = 1


class RoundBottomDescriptor(BaseSchemaVersionedModelV1):
    """:class:``RoundBottomDescription`` with optional parameters."""

    type: Literal["Round"] = "Round"
    schema_version: Literal[1] = 1
