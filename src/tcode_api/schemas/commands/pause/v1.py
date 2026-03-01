from typing import Literal

from ..base import BaseTCodeCommand


class PAUSE_V1(BaseTCodeCommand):
    """Pause execution until manually resumed."""

    type: Literal["PAUSE"] = "PAUSE"
    schema_version: Literal[1] = 1
