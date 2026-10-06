from typing import Annotated

from pydantic import Field

from .labware_holder_name.latest import LabwareHolderName
from .labware_id.latest import LabwareId
from .module_id.latest import ModuleId

LabwareHolder = Annotated[
    LabwareHolderName | LabwareId | ModuleId,
    Field(
        discriminator="type", description="Union type of all valid LabwareHolder specifications."
    ),
]
