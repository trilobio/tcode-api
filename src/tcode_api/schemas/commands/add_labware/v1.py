from typing import Literal

from pydantic import Field

from ...descriptions.labware.union import LabwareDescriptor
from ..base import BaseTCodeCommand


class ADD_LABWARE_V1(BaseTCodeCommand):
    """Find a matching labware on the fleet and assign it the given id.

    :raises ValidatorError: ``ValidatorErrorCode.ID_EXISTS`` if ``id`` is already registered to
        a labware.
    """

    type: Literal["ADD_LABWARE"] = "ADD_LABWARE"
    schema_version: Literal[1] = 1

    id: str = Field(
        description=(
            "Identifier to assign to the resolved labware. "
            "This id is used in subsequent commands to reference this labware."
        )
    )
    descriptor: LabwareDescriptor = Field(
        description="Minimal descriptor of the desired labware; resolved on the fleet."
    )
    lid_id: str | None = Field(
        default=None,
        description=(
            "Optional identifier to assign to a lid associated with the labware. "
            "If provided, the labware descriptor must indicate that the labware has a lid."
        ),
    )
