from typing import Literal

from pydantic import Field

from ...location.union import Location
from ..base import BaseRobotSpecificTCodeCommand


class PICK_UP_PIPETTE_TIP_V1(BaseRobotSpecificTCodeCommand):
    """Pick up pipette tip(s) at the specified location."""

    type: Literal["PICK_UP_PIPETTE_TIP"] = "PICK_UP_PIPETTE_TIP"
    schema_version: Literal[1] = 1

    location: Location = Field(description="Location at which to pick up the pipette tip(s).")
