from typing import Literal

from ..base import BaseToolDescriptor


class GripperDescriptorV1(BaseToolDescriptor):

    type: Literal["Gripper"] = "Gripper"
    schema_version: Literal[1] = 1
