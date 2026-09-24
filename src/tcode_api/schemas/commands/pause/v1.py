from typing import Literal

from ..base.tcode_command.v1 import BaseTCodeCommandV1


class PAUSE(BaseTCodeCommandV1):
    """Pause execution until manually resumed."""

    type: Literal["PAUSE"] = "PAUSE"
    schema_version: Literal[1] = 1
