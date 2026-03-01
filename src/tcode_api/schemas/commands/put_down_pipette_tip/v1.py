from typing import Literal

from pydantic import Field

from ...location.union import Location
from ..base import BaseRobotSpecificTCodeCommand


class PUT_DOWN_PIPETTE_TIP_V1(BaseRobotSpecificTCodeCommand):
    """Put down the currently held pipette tip(s)."""

    type: Literal["PUT_DOWN_PIPETTE_TIP"] = "PUT_DOWN_PIPETTE_TIP"
    schema_version: Literal[1] = 1

    location: Location = Field(description="Location at which to put down the pipette tip(s).")
