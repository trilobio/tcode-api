"""BaseConfiguredModel v1."""

from abc import ABC

from pydantic import BaseModel, ConfigDict


class BaseConfiguredModelV1(BaseModel, ABC):
    """pydantic.BaseModel with configuration to apply to all TCode data structures.

    All TCode data structures should inherit from this class to ensure consistent
    configuration.
    """

    model_config = ConfigDict(strict=True, extra="ignore")
