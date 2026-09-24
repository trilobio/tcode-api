from typing import Literal

from pydantic import Field

from ..base.location.v1 import BaseLocationV1


class LocationAsNodeId(BaseLocationV1):
    """Location specified by a node ID in the fleet's ``TransformTree``."""

    type: Literal["LocationAsNodeId"] = "LocationAsNodeId"
    schema_version: Literal[1] = 1

    node_id: str = Field(
        description=(
            "ID of the node in the fleet's ``TransformTree`` to target. "
            "This command is primarily intended for debugging, "
            "as it requires separate access to the fleet's internal ``TransformTree`` server."
        ),
    )
