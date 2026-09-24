"""BaseTCodeCommand v1."""

from abc import ABC

from ....base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1
from ....common.docs import TypeField


class BaseTCodeCommandV1(BaseSchemaVersionedModelV1, ABC):
    """Base schema shared by all TCode commands in the TCODE discriminated union.

    :raises ValidatorError: ``ValidatorErrorCode.INTERNAL_ERROR`` if any unexpected error occurs
        during validation. If this occurs, file an issue on
        https://github.com/trilobio/tcode-api/issues.
    """

    type: TypeField
