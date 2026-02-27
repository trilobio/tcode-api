"""Base classes for specifying LabwareHolders in TCode."""

from abc import ABC

from ..base import BaseSchemaVersionedModel
from ..common.docs import TypeField


class BaseLabwareHolder(BaseSchemaVersionedModel, ABC):
    """Base schema shared by all models in the LabwareHolder discriminated union."""

    type: TypeField
