from typing import Literal

from pydantic import Field

from ..base import BaseLocation


class LocationAsNodeIdV1(BaseLocation):
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
