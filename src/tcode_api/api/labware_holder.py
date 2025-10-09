"""LabwareHolder Interface, which contains multiple options for describing a labware holder."""

from typing import Annotated, Literal

from pydantic import Field

from tcode_api.api.core import _ConfiguredBaseModel


class _LabwareHolderBase(_ConfiguredBaseModel):
    """Base schema shared by all models in the LabwareHOlder discriminated union."""

    type: str


class LabwareHolderName(_LabwareHolderBase):
    """Name of a labware holder on the deck of a targeted robot."""

    type: Literal["LabwareHolderName"] = "LabwareHolderName"
    robot_id: str
    name: str


class LabwareId(_LabwareHolderBase):
    """Id of a labware that can hold another labware."""

    type: Literal["LabwareId"] = "LabwareId"
    id: str


LabwareHolder = Annotated[
    LabwareHolderName | LabwareId,
    Field(discriminator="type"),
]
