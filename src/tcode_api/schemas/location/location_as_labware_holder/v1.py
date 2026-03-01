from typing import Literal

from pydantic import Field

from ..base import BaseLocation


class LocationAsLabwareHolderV1(BaseLocation):
    """Location specified by a labware holder's name."""

    type: Literal["LocationAsLabwareHolder"] = "LocationAsLabwareHolder"
    schema_version: Literal[1] = 1

    robot_id: str = Field(description="ID of the robot on which the labware holder is located.")

    labware_holder_name: str = Field(
        description=(
            "Name of the labware holder, as defined in the robot's configuration. "
            'Most often, this will be a deck slot in the format "DeckSlot_#".'
        ),
    )
