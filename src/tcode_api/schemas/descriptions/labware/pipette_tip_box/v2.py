from typing import Literal

from pydantic import Field

from ....pipette_tip_layout.v1 import PipetteTipLayoutV1
from ...grid.v1 import GridDescriptionV1, GridDescriptorV1
from ...pipette_tip.v1 import PipetteTipDescriptionV1, PipetteTipDescriptorV1
from ..base import BaseLabwareDescription, BaseLabwareDescriptor

grid_description = "Layout of the pipette tip box slots. typically an 8*12 grid for a 96 tip box."

pipette_tip_description = (
    "Description of the pipette tips used in the box. "
    "All pipette tips are assumed to be identical."
)
pipette_tip_layout_description = (
    "Specifies which slots contain pipette tips."
    "If not provided, it is assumed that all slots in the grid are filled with pipette tips."
)


class PipetteTipBoxDescriptionV2(BaseLabwareDescription):
    """Description of a pipette tip box."""

    type: Literal["PipetteTipBox"] = "PipetteTipBox"
    schema_version: Literal[2] = 2

    grid: GridDescriptionV1 = Field(
        description=grid_description,
    )
    pipette_tip: PipetteTipDescriptionV1 = Field(
        description=pipette_tip_description,
    )
    pipette_tip_layout: PipetteTipLayoutV1 = Field(
        default_factory=PipetteTipLayoutV1.full,
        description=pipette_tip_layout_description,
    )


def migrate_v1_to_v2(data: dict) -> dict:
    """Migrate :class:``PipetteTipBoxDescription``|:class:``PipetteTipBoxDescriptor`` data from v1 to v2."""
    # This logic allows data with no `schema_version` defined, which is fine, because older models didn't have that!
    # We're assuming that all older models are version 1.
    if "schema_version" in data and data["schema_version"] != 0:
        raise ValueError(
            f"Cannot migrate PipetteTipBoxDescription from version {data['schema_version']} to version 2"
        )

    new_data = {
        "type": "PipetteTipBox",
        "schema_version": 1,
        "grid": data["grid"],
        "pipette_tip": data["pipette_tip"],
    }
    if data["full"] is None:
        new_data["pipette_tip_layout"] = None
    elif data["full"] is True:
        new_data["pipette_tip_layout"] = PipetteTipLayoutV1.full()
    else:
        new_data["pipette_tip_layout"] = PipetteTipLayoutV1.empty()
    return new_data


class PipetteTipBoxDescriptorV2(BaseLabwareDescriptor):
    """PipetteTipBoxDescription with optional parameters."""

    type: Literal["PipetteTipBox"] = "PipetteTipBox"
    schema_version: Literal[2] = 2

    grid: GridDescriptorV1 | None = Field(
        default=None,
        description=grid_description,
    )
    pipette_tip: PipetteTipDescriptorV1 | None = Field(
        default=None,
        description=pipette_tip_description,
    )
    pipette_tip_layout: PipetteTipLayoutV1 | None = Field(
        default=None,
        description=pipette_tip_layout_description,
    )
