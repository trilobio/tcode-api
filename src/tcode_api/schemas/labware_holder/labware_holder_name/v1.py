from typing import Literal

from pydantic import Field

from ..base import BaseLabwareHolder


class LabwareHolderNameV1(BaseLabwareHolder):
    """LabwareHolder specified by name and target robot."""

    type: Literal["LabwareHolderName"] = "LabwareHolderName"
    schema_version: Literal[1] = 1

    robot_id: str = Field(
        description=(
            "TCode-assigned robot id. " "Assigned previously with :class:``ADD_ROBOT`` command. "
        ),
    )
    name: str = Field(
        description=(
            "Name of the labware holder, as defined in the robot's configuration. "
            'Most often, this will be a deck slot in the format "DeckSlot_#".'
        ),
    )
