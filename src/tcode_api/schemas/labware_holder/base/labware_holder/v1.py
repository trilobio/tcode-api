"""BaseLabwareHolder v1."""

from abc import ABC

from ....base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1
from ....common.docs import TypeField


class BaseLabwareHolderV1(BaseSchemaVersionedModelV1, ABC):
    """Base schema shared by all models in the LabwareHolder discriminated union."""

    type: TypeField
