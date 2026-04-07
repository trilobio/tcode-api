from typing import Literal

from ..base import BaseToolDescriptor


class ProbeDescriptor(BaseToolDescriptor):

    type: Literal["Probe"] = "Probe"
    schema_version: Literal[1] = 1
