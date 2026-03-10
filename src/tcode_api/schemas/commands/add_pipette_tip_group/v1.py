from typing import Literal

from pydantic import Field

from ...descriptions.pipette_tip_group.v1 import PipetteTipGroupDescriptorV1
from ..base import BaseTCodeCommand


class ADD_PIPETTE_TIP_GROUP_V1(BaseTCodeCommand):
    """Find a matching group of pipette tips on the fleet and assign it the given id.

    :raises ValidatorError: ``ValidatorErrorCode.ID_EXISTS`` if ``id`` is already registered to
        a pipette tip group.
    """

    type: Literal["ADD_PIPETTE_TIP_GROUP"] = "ADD_PIPETTE_TIP_GROUP"
    schema_version: Literal[1] = 1

    id: str = Field(
        description=(
            "Identifier to assign to the resolved pipette tip group. "
            "This id is used in subsequent commands to reference this pipette tip group."
        )
    )

    descriptor: PipetteTipGroupDescriptorV1 = Field(
        description=("Minimal descriptor of the desired pipette tip group; resolved on the fleet.")
    )
