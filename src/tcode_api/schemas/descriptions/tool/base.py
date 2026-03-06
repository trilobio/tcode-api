"""Base classes for descriptions and descriptors of TCode tool entities."""

from abc import ABC

from ..base import BaseDescriberWithSerialNumber


class BaseToolDescriptor(BaseDescriberWithSerialNumber, ABC):
    """Base schema shared by all models in the ToolDescriptor union."""
