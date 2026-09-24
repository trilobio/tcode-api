"""BaseToolDescriptor v1."""

from abc import ABC

from ....base.describer_with_serial_number.v1 import BaseDescriberWithSerialNumberV1


class BaseToolDescriptorV1(BaseDescriberWithSerialNumberV1, ABC):
    """Base schema shared by all models in the ToolDescriptor union."""
