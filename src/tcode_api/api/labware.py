"""Data structures for describing labware entities in TCode."""

import enum
from typing import Annotated, Literal

from pydantic import Field

from tcode_api.api.core import (
    AxisAlignedRectangleDescription,
    AxisAlignedRectangleDescriptor,
    CircleDescription,
    CircleDescriptor,
    ValueWithUnits,
    _ConfiguredBaseModel,
    _verify_positive_nonzero_int,
)
from tcode_api.types import NamedTags, Tags


# Components for describing wells
class WellPartType(enum.StrEnum):
    """Enumeration of well parts.

    TOP: the top part of the well, above the liquid level.
    BOTTOM: the bottom part of the well, below the liquid level.
    """

    TOP = "TOP"
    BOTTOM = "BOTTOM"


WellShapeDescription = Annotated[
    CircleDescription | AxisAlignedRectangleDescription,
    Field(discriminator="type"),
]
WellShapeDescriptor = Annotated[
    CircleDescriptor | AxisAlignedRectangleDescriptor,
    Field(discriminator="type"),
]


# Well Bottom Profiles
class FlatBottomDescriptor(_ConfiguredBaseModel):
    """Descriptor for a flat bottom well."""

    type: Literal["Flat"] = "Flat"


class FlatBottomDescription(FlatBottomDescriptor):
    """FlatBottomDescription with optional paramters."""


class RoundBottomDescription(_ConfiguredBaseModel):
    """Descriptor for a round bottom well."""

    type: Literal["Round"] = "Round"
    # radius: the radius is inferred from the well's diameter


class RoundBottomDescriptor(_ConfiguredBaseModel):
    """RoundBottomDescription with optional parameters."""

    type: Literal["Round"] = "Round"


class VBottomDescription(_ConfiguredBaseModel):
    """Description of a V-bottom well (think trough)."""

    type: Literal["V-Shape"] = "V-Shape"
    direction: Literal["x-axis", "y-axis"]
    offset: ValueWithUnits


class VBottomDescriptor(_ConfiguredBaseModel):
    """VBottomDescription with optional parameters."""

    type: Literal["V-Shape"] = "V-Shape"
    direction: Literal["x-axis", "y-axis"] | None = None
    offset: ValueWithUnits | None = None


class ConicalBottomDescription(_ConfiguredBaseModel):
    """Description of a conical bottom well."""

    type: Literal["Conical"] = "Conical"
    # angle: assumed to come to a point at the bottom of the well
    offset: ValueWithUnits


class ConicalBottomDescriptor(_ConfiguredBaseModel):
    """ConicalBottomDescription with optional parameters."""

    type: Literal["Conical"] = "Conical"
    offset: ValueWithUnits | None = None


WellBottomShapeDescription = Annotated[
    ConicalBottomDescription
    | FlatBottomDescription
    | RoundBottomDescription
    | VBottomDescription,
    Field(discriminator="type"),
]
WellBottomShapeDescriptor = Annotated[
    ConicalBottomDescriptor
    | FlatBottomDescriptor
    | RoundBottomDescriptor
    | VBottomDescriptor,
    Field(discriminator="type"),
]


# Wells
class WellDescription(_ConfiguredBaseModel):
    """Description of a well in a labware."""

    type: Literal["Well"] = "Well"
    depth: ValueWithUnits
    shape: WellShapeDescription
    bottom_shape: WellBottomShapeDescription
    min_volume: ValueWithUnits
    max_volume: ValueWithUnits
    well_tags: Tags = Field(default_factory=list)
    well_named_tags: NamedTags = Field(default_factory=dict)


class WellDescriptor(_ConfiguredBaseModel):
    """WellDescription with optional parameters."""

    type: Literal["Well"] = "Well"
    depth: ValueWithUnits | None = None
    shape: WellShapeDescriptor | None = None
    bottom_shape: WellBottomShapeDescriptor | None = None
    min_volume: ValueWithUnits | None = None
    max_volume: ValueWithUnits | None = None


# Grids of wells
class GridDescription(_ConfiguredBaseModel):
    """Description of a grid layout."""

    type: Literal["Grid"] = "Grid"
    row_count: int
    column_count: int
    row_pitch: ValueWithUnits
    column_pitch: ValueWithUnits
    row_offset: ValueWithUnits
    column_offset: ValueWithUnits


class GridDescriptor(_ConfiguredBaseModel):
    """GridDescription with optional parameters."""

    type: Literal["Grid"] = "Grid"
    row_count: int | None = None
    column_count: int | None = None
    row_pitch: ValueWithUnits | None = None
    column_pitch: ValueWithUnits | None = None
    row_offset: ValueWithUnits | None = None
    column_offset: ValueWithUnits | None = None


# Non-plate labware
class PipetteTipDescription(_ConfiguredBaseModel):
    """Description of a pipette tip."""

    type: Literal["PipetteTip"] = "PipetteTip"
    tags: Tags = Field(default_factory=list)
    named_tags: NamedTags = Field(default_factory=dict)
    has_filter: bool
    height: ValueWithUnits
    flange_height: ValueWithUnits
    max_volume: ValueWithUnits
    min_volume: ValueWithUnits


class PipetteTipDescriptor(_ConfiguredBaseModel):
    """PipetteTipDescription with optional parameters."""

    type: Literal["PipetteTip"] = "PipetteTip"
    tags: Tags = Field(default_factory=list)
    named_tags: NamedTags = Field(default_factory=dict)
    has_filter: bool | None = None
    height: ValueWithUnits | None = None
    flange_height: ValueWithUnits | None = None
    max_volume: ValueWithUnits | None = None
    min_volume: ValueWithUnits | None = None


class PipetteTipGroupDescriptor(_ConfiguredBaseModel):
    """PipetteTipGroupDescription with optional parameters."""

    type: Literal["PipetteTipGroup"] = "PipetteTipGroup"

    row_count: Annotated[int, _verify_positive_nonzero_int]
    column_count: Annotated[int, _verify_positive_nonzero_int]
    pipette_tip_tags: Tags = Field(default_factory=list)
    pipette_tip_named_tags: NamedTags = Field(default_factory=dict)


class TubeDescription(_ConfiguredBaseModel):
    """Description of a tube."""

    type: Literal["Tube"] = "Tube"
    tags: Tags = Field(default_factory=list)
    named_tags: NamedTags = Field(default_factory=dict)
    depth: ValueWithUnits
    shape: WellShapeDescription
    bottom_shape: WellBottomShapeDescription
    min_volume: ValueWithUnits
    max_volume: ValueWithUnits
    top_height: ValueWithUnits


class TubeDescriptor(_ConfiguredBaseModel):
    """TubeDescription with optional parameters."""

    type: Literal["Tube"] = "Tube"
    tags: Tags = Field(default_factory=list)
    named_tags: NamedTags = Field(default_factory=dict)
    depth: ValueWithUnits | None = None
    shape: WellShapeDescriptor | None = None
    bottom_shape: WellBottomShapeDescriptor | None = None
    min_volume: ValueWithUnits | None = None
    max_volume: ValueWithUnits | None = None
    top_height: ValueWithUnits | None = None


# Plate Labware
class _LabwareBaseDescription(_ConfiguredBaseModel):
    """Base schema shared by all labware in the Labware discriminated union.

    :note: Using [x|y|z]_length is intended to avoid the semantic ambiguity of "length" vs "width"
    """

    tags: Tags = Field(default_factory=list)
    named_tags: NamedTags = Field(default_factory=dict)
    x_length: ValueWithUnits
    y_length: ValueWithUnits
    z_length: ValueWithUnits


class _LabwareBaseDescriptor(_ConfiguredBaseModel):
    """Base schema shared by all labware descriptors in the LabwareDescriptor discriminated union."""

    tags: Tags = Field(default_factory=list)
    named_tags: NamedTags = Field(default_factory=dict)
    x_length: ValueWithUnits | None = None
    y_length: ValueWithUnits | None = None
    z_length: ValueWithUnits | None = None


class LidDescription(_LabwareBaseDescription):
    """Description of a plate lid."""

    type: Literal["Lid"] = "Lid"
    stackable: bool


class LidDescriptor(_LabwareBaseDescriptor):
    """LidDescription with optional parameters."""

    type: Literal["Lid"] = "Lid"
    stackable: bool | None = None


class WellPlateDescription(_LabwareBaseDescription):
    """Description of a well plate.

    :note: The exception to the 'no optional attributes' rule is `lid_offset` and `lid`.
        These attributes default to None, assuming that a described labware has no lid.
    """

    type: Literal["WellPlate"] = "WellPlate"
    grid: GridDescription
    well: WellDescription

    # Lid parameters
    lid_offset: ValueWithUnits | None = None
    lid: LidDescription | None = None


class WellPlateDescriptor(_LabwareBaseDescriptor):
    """WellPlateDescription with optional parameters."""

    type: Literal["WellPlate"] = "WellPlate"
    grid: GridDescriptor | None = None
    well: WellDescriptor | None = None
    lid_offset: ValueWithUnits | None = None
    lid: LidDescriptor | None = None


class PipetteTipBoxDescription(_LabwareBaseDescription):
    """Description of a pipette tip box."""

    type: Literal["PipetteTipBox"] = "PipetteTipBox"
    grid: GridDescription
    full: bool
    pipette_tip: PipetteTipDescription


class PipetteTipBoxDescriptor(_LabwareBaseDescriptor):
    """PipetteTipBoxDescription with optional parameters."""

    type: Literal["PipetteTipBox"] = "PipetteTipBox"
    grid: GridDescriptor | None = None
    full: bool | None = None
    pipette_tip: PipetteTipDescriptor | None = None


class TubeHolderDescription(_LabwareBaseDescription):
    """Description of a tube holder."""

    type: Literal["TubeHolder"] = "TubeHolder"
    grid: GridDescription
    tube: TubeDescription


class TubeHolderDescriptor(_LabwareBaseDescriptor):
    """TubeHolderDescription with optional parameters."""

    type: Literal["TubeHolder"] = "TubeHolder"
    grid: GridDescriptor | None = None
    tube: TubeDescriptor | None = None


class TrashDescription(_LabwareBaseDescription):
    """Description of a waste disposal container."""

    type: Literal["Trash"] = "Trash"
    well: WellDescription


class TrashDescriptor(_LabwareBaseDescriptor):
    """TrashDescription with optional parameters."""

    type: Literal["Trash"] = "Trash"
    well: WellDescriptor | None = None


LabwareDescription = Annotated[
    LidDescription
    | PipetteTipBoxDescription
    | TrashDescription
    | TubeHolderDescription
    | WellPlateDescription,
    Field(discriminator="type"),
]
LabwareDescriptor = Annotated[
    LidDescriptor
    | PipetteTipBoxDescriptor
    | TrashDescriptor
    | TubeHolderDescriptor
    | WellPlateDescriptor,
    Field(discriminator="type"),
]
