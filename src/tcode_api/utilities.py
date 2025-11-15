"""Helpful constructors for common tcode_api objects."""

import functools
import json
import pathlib
import random
import site
import string

from pydantic import TypeAdapter

import tcode_api.api as tc
from tcode_api.types import Matrix, NamedTags, Tags, UnsanitizedFloat

DEFAULT_LABWARE_DIR = "tcode_labware"

# Compute whether the current file is included in site-packages
# as this affects where the default labware distribution is
current_path = pathlib.Path(__file__)
for p in site.getsitepackages():
    site_path = pathlib.Path(p)
    if current_path.is_relative_to(site_path):
        DEFAULT_LABWARE_PATH = site_path / DEFAULT_LABWARE_DIR
        break
else:
    DEFAULT_LABWARE_PATH = current_path.parent.parent.parent / DEFAULT_LABWARE_DIR


class LabwareIO:
    """Class for reading/writing labware descriptions from storage."""

    def __init__(self, labware_dir: pathlib.Path | None = None) -> None:
        """Initialize LabwareIO."""
        if labware_dir is None:
            self.labware_dir = DEFAULT_LABWARE_PATH

        if not self.labware_dir.exists():
            raise FileNotFoundError(
                f"Labware directory not found: {self.labware_dir}. Please check whether tcode is installed correctly."
            )

        self.labware_type_adapter: TypeAdapter = TypeAdapter(tc.LabwareDescription)

    def _resolve_file_path(
        self, file_path: str | pathlib.Path, exists: bool | None = None
    ) -> pathlib.Path:
        """Resolve file path to labware description file.

        :param file_path: Name of file or path to file containing description. If file_path is a string,
            checks tcode_api/labware for a file whose name matches file_path. If no such file exists,
            file_path is cast to a pathlib Path.
        :param exists: If True, raises FileNotFoundError if the resolved file does not exist. If
            False, does not check for existence. If None, doesn't check file existence.
        :return: Resolved pathlib.Path to the labware description file.
        """
        if isinstance(file_path, str):
            file_path = self.labware_dir / f"{file_path}.json"
            if not file_path.exists():
                file_path = pathlib.Path(file_path)

        if exists is True and not file_path.exists():
            raise FileNotFoundError(f"Labware file not found: {file_path}")
        if exists is False and file_path.exists():
            raise FileExistsError(f"Labware file already exists: {file_path}")
        return file_path

    def load(self, identifier: str | pathlib.Path) -> tc.LabwareDescription:
        """Read labware description from JSON file.

        :param identifier: Name of file or path to file containing description. If file_path is a string,
            checks tcode_api/labware for a file whose name matches file_path. If no such file exists,
            file_path is cast to a pathlib Path.
        :return: tc.LabwareDescription loaded from the file.
        """
        file_path = self._resolve_file_path(identifier, exists=True)
        with file_path.open("r", encoding="utf-8") as f:
            data = f.read()

        model_constructor = self.labware_type_adapter.validate_python(json.loads(data))
        return model_constructor.model_validate_json(data)

    def write(self, identifier: str | pathlib.Path, labware: tc.LabwareDescription) -> None:
        """Write labware description to JSON file.

        :param identifier: Path to file where description will be written.
        :param labware: tc.LabwareDescription to write to file.
        """
        file_path = pathlib.Path(identifier)
        with file_path.open("w", encoding="utf-8") as f:
            f.write(labware.model_dump_json(indent=2))


def load_labware(
    identifier: str | pathlib.Path, labware_dir: pathlib.Path | None = None
) -> tc.LabwareDescription:
    """Return LabwareDescription object loaded from file source.

    :param identifier: Name of labware or path to file containing description. If file_path is a string,
        checks tcode_api/labware for a file whose name matches file_path. If no such file exists,
        file_path is cast to a pathlib Path.
    :param labware_dir: Path to labware directory. If None, defaults to tcode_api/labware.

    :return: loaded tc.LabwareDescription.
    """
    labware_io = LabwareIO(labware_dir=labware_dir)
    return labware_io.load(identifier)


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


def s(seconds: UnsanitizedFloat) -> tc.ValueWithUnits:
    """tc.ValueWithUnits constructor for seconds.

    :return: tc.ValueWithUnits with magnitude in s.
    """
    return tc.ValueWithUnits(magnitude=_cast_to_float(seconds), units="s")


def create_transform(
    x: tc.ValueWithUnits | None = None,
    y: tc.ValueWithUnits | None = None,
    z: tc.ValueWithUnits | None = None,
    a: tc.ValueWithUnits | None = None,
    b: tc.ValueWithUnits | None = None,
    c: tc.ValueWithUnits | None = None,
) -> Matrix:
    """Factory function for creating transformation matrices.

    :param x: translation in x direction; defaults to 0.
    :param y: translation in y direction; defaults to 0.
    :param z: translation in z direction; defaults to 0.
    :param a: rotation about z axis in radians; defaults to 0.
    :param b: rotation about y axis in radians; defaults to 0.
    :param c: rotation about x axis in radians; defaults to 0.

    :return: tc.Matrix representing a transformation matrix for the specified transformation.
    """
    if b is not None or c is not None:
        raise NotImplementedError(
            "Rotation about x and y axes not yet implemented in create_transform"
        )

    if x is None:
        x = tc.ValueWithUnits(magnitude=0.0, units="m")
    if y is None:
        y = tc.ValueWithUnits(magnitude=0.0, units="m")
    if z is None:
        z = tc.ValueWithUnits(magnitude=0.0, units="m")
    if a is None:
        a = tc.ValueWithUnits(magnitude=0.0, units="radians")

    return [
        [1.0, 0.0, 0.0, x.to("m").magnitude],
        [0.0, 1.0, 0.0, y.to("m").magnitude],
        [0.0, 0.0, 1.0, z.to("m").magnitude],
        [0.0, 0.0, 0.0, 1.0],
    ]


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
