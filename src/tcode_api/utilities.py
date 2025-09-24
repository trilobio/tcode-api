"""Helpful constructors for common tcode_api objects."""

import functools
import random
import string

import tcode_api.api as tc
from tcode_api.types import NamedTags, Tags, UnsanitizedFloat


def generate_id(length: int = 22) -> str:
    """Generate random string for use as id.

    :param length: Length of the generated string, default is 22.

    :return: generated string
    """
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def _cast_to_float(value: UnsanitizedFloat) -> float:
    """Cast int to float or try to parse string as float."""
    if isinstance(value, (float, int)):
        return float(value)
    try:
        return float(value)
    except ValueError as e:
        raise ValueError(f"Cannot convert {value} to float") from e


def mm(length: UnsanitizedFloat) -> tc.ValueWithUnits:
    """tc.ValueWithUnits constructor for millimeters.

    :return: tc.ValueWithUnits with magnitude in mm.
    """
    return tc.ValueWithUnits(magnitude=_cast_to_float(length), units="mm")


def m(length: UnsanitizedFloat) -> tc.ValueWithUnits:
    """tc.ValueWithUnits constructor for meters.

    :return: tc.ValueWithUnits with magnitude in m.
    """
    return tc.ValueWithUnits(magnitude=_cast_to_float(length), units="m")


def rad(angle: UnsanitizedFloat) -> tc.ValueWithUnits:
    """tc.ValueWithUnits constructor for radians.

    :return: tc.ValueWithUnits with magnitude in rad.
    """
    return tc.ValueWithUnits(magnitude=_cast_to_float(angle), units="rad")


def ul(volume: UnsanitizedFloat) -> tc.ValueWithUnits:
    """tc.ValueWithUnits constructor for uL.

    :return: tc.ValueWithUnits with magnitude in uL.
    """
    return tc.ValueWithUnits(magnitude=_cast_to_float(volume), units="uL")


def ul_per_s(volume: UnsanitizedFloat) -> tc.ValueWithUnits:
    """tc.ValueWithUnits constructor for uL/s.

    :return: tc.ValueWithUnits with magnitude in uL/s.
    """
    return tc.ValueWithUnits(magnitude=_cast_to_float(volume), units="uL/s")


def location_as_labware_index(
    labware_id: str,
    location_index: int,
    well_part: str | tc.WellPartType | None = None,
) -> tc.LocationAsLabwareIndex:
    """tc.LocationAsLabwareIndex constructor.

    :note: defaults to the bottom of the well
    """
    well_part = well_part or tc.WellPartType.BOTTOM
    if isinstance(well_part, str):
        well_part = tc.WellPartType(well_part)
    return tc.LocationAsLabwareIndex(
        labware_id=labware_id,
        location_index=location_index,
        well_part=well_part,
    )


def describe_well_plate(
    tags: Tags | None = None,
    named_tags: NamedTags | None = None,
    row_count: int = 8,
    column_count: int = 12,
    row_pitch: float = 0.009,
    column_pitch: float = 0.009,
    has_lid: bool = False,
) -> tc.WellPlateDescriptor:
    """tc.WellPlateDescriptor constructor with nice defaults.

    :param tags: List of tags associated with the well plate. Defaults to an empty list.
    :param named_tags: Dictionary of named tags associated with the well plate. Defaults to an empty dictionary.
    :param row_count: Number of rows in the well plate. Defaults to 8.
    :param column_count: Number of columns in the well plate. Defaults to 12.
    :param row_pitch: Pitch between rows in meters. Defaults to 0.009 m.
    :param column_pitch: Pitch between columns in meters. Defaults to 0.009 m.
    :param has_lid: Whether the well plate has a lid. Defaults to False.

    :return: tc.WellPlateDescriptor constructed with the specified parameters.
    """
    tags = [] if tags is None else tags
    named_tags = {} if named_tags is None else named_tags
    grid_descriptor = tc.GridDescriptor(
        row_count=row_count,
        column_count=column_count,
        row_pitch=m(row_pitch),
        column_pitch=m(column_pitch),
    )
    lid_descriptor = tc.LidDescriptor() if has_lid else None
    return tc.WellPlateDescriptor(
        tags=tags,
        named_tags=named_tags,
        grid=grid_descriptor,
        has_lid=has_lid,
        lid=lid_descriptor,
    )


def describe_pipette_tip_box(
    tags: Tags | None = None,
    named_tags: NamedTags | None = None,
    row_count: int = 8,
    column_count: int = 12,
    row_pitch: float = 0.009,
    column_pitch: float = 0.009,
    full: bool = True,
) -> tc.PipetteTipBoxDescriptor:
    """tc.PipetteTipBoxDescriptor constructor with nice defaults.

    :param tags: List of tags associated with the pipette tip box. Defaults to an empty list.
    :param named_tags: Dictionary of named tags associated with the pipette tip box. Defaults to an empty dictionary.
    :param row_count: Number of rows in the pipette tip box. Defaults to 8.
    :param column_count: Number of columns in the pipette tip box. Defaults to 12.
    :param row_pitch: Pitch between rows in meters. Defaults to 0.009 m.
    :param column_pitch: Pitch between columns in meters. Defaults to 0.009 m.
    :param full: Whether the pipette tip box is full of tips. Defaults to True.

    :return: tc.PipetteTipBoxDescriptor constructed with the specified parameters.
    """
    tags = [] if tags is None else tags
    named_tags = {} if named_tags is None else named_tags
    grid_descriptor = tc.GridDescriptor(
        row_count=row_count,
        column_count=column_count,
        row_pitch=m(row_pitch),
        column_pitch=m(column_pitch),
    )
    return tc.PipetteTipBoxDescriptor(
        tags=tags,
        named_tags=named_tags,
        grid=grid_descriptor,
        full=full,
    )


def describe_pipette_tip_group(
    row_count: int = 1,
    column_count: int = 1,
    tags: Tags | None = None,
    named_tags: NamedTags | None = None,
) -> tc.PipetteTipGroupDescriptor:
    """tc.PipetteTipGroup constructor with nice defaults.

    :param row_count: Number of rows in the pipette tip group. Defaults to 1.
    :param column_count: Number of columns in the pipette tip group. Defaults to 1.
    :param tags: List of tags applied to each pipette tip in the pipette tip group. Defaults to an empty list.
    :param named_tags: Dictionary of named tags applied to each pipette tip in the pipette tip group. Defaults to an empty dictionary.

    :return: tc.PipetteTipGroup constructed with the specified parameters.
    """
    return tc.PipetteTipGroupDescriptor(
        row_count=row_count,
        column_count=column_count,
        pipette_tip_tags=tags or [],
        pipette_tip_named_tags=named_tags or {},
    )


describe_pipette_tip_1x1 = functools.partial(
    describe_pipette_tip_group, row_count=1, column_count=1
)
describe_pipette_tip_1x1.__doc__ = (
    "tc.PipetteTipGroup constructor for a single pipette tip.\n\n"
    "param id: Unique identifier for the pipette tip group. Defaults to generate_id().\n"
    "param tags: List of tags applied to the pipette tip. Defaults to an empty list.\n"
    "param named_tags: Dictionary of named tags applied to the pipette tip. Defaults to an empty dictionary.\n\n"
    "return: tc.PipetteTipGroup with 1 row and 1 column."
)
describe_pipette_tip_1x8 = functools.partial(
    describe_pipette_tip_group, row_count=1, column_count=8
)
describe_pipette_tip_1x8.__doc__ = (
    "tc.PipetteTipGroup constructor for an 8-channel pipette tip group.\n\n"
    "param id: Unique identifier for the pipette tip group. Defaults to generate_id().\n"
    "param tags: List of tags applied to the pipette tip. Defaults to an empty list.\n"
    "param named_tags: Dictionary of named tags applied to the pipette tip. Defaults to an empty dictionary.\n\n"
    "return: tc.PipetteTipGroup with 1 row and 8 columns."
)
