from typing import Literal

from pydantic import Field

from ..base import BaseLocation


class LocationAsLabwareIndexV1(BaseLocation):
    """Location specifed as a specific feature of a Labware (ex. bottom of well A1)."""

    type: Literal["LocationAsLabwareIndex"] = "LocationAsLabwareIndex"
    schema_version: Literal[1] = 1

    labware_id: str = Field(
        description=(
            "TCode ID of the labware to target, "
            "assigned previously by the :class:``ADD_LABWARE`` command."
        ),
    )
    location_index: int = Field(
        description=(
            'Index into labware "slots". In a 96-well plate, for example, '
            "this index operates in row-major order (A1 is 0, A12 is 11, H12 is 95)."
        ),
    )
    well_part: str = Field(
        description=(
            "String instance of :class:``WellPartType``. "
            "Allows targeting of the top or bottom of a well selected with the ``location_index``."
        ),
    )
