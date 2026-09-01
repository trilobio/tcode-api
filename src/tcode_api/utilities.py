"""Helpful constructors for common tcode_api objects."""

import base64
import functools
import json
import pathlib
import site
import uuid
from typing import cast

import numpy as np
from scipy.spatial.transform import Rotation  # type: ignore[import-untyped]

import tcode_api.api as tc
from tcode_api.api.compat import migrate_data_to_latest
from tcode_api.schemas.base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1
from tcode_api.schemas.registry import schema_registry
from tcode_api.types import Matrix, UnsanitizedFloat

SCIPY_SEQ = "zyx"  # Extrinsic rotation sequence
SCIPY_DEGREES = False  # Angles are in radians


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


class SchemaIO:
    """Class for reading/writing any registered tcode_api schema from/to storage.

    Unlike a fixed-type loader, each file is dispatched by its own ``"type"`` discriminator via
    ``schema_registry``, so a single instance can read a directory containing a mix of schema
    kinds (e.g. ``tcode_labware/`` mixes labware descriptions with nested ``PipetteTip`` files).
    """

    def __init__(self, schema_dir: pathlib.Path | None = None) -> None:
        """Initialize SchemaIO."""
        if schema_dir is None:
            self.schema_dir = DEFAULT_LABWARE_PATH
        else:
            self.schema_dir = pathlib.Path(schema_dir)

        if not self.schema_dir.exists():
            raise FileNotFoundError(
                f"Schema directory not found: {self.schema_dir}. Please check whether tcode is installed correctly."
            )

    def _resolve_file_path(
        self, file_path: str | pathlib.Path, exists: bool | None = None
    ) -> pathlib.Path:
        """Resolve file path to a schema file.

        :param file_path: Name of file or path to file containing schema data. If file_path is a
            string, checks ``self.schema_dir`` for a file whose name matches file_path. If no
            such file exists, file_path is cast to a pathlib Path.
        :param exists: If True, raises FileNotFoundError if the resolved file does not exist. If
            False, does not check for existence. If None, doesn't check file existence.
        :return: Resolved pathlib.Path to the schema file.
        """
        if isinstance(file_path, str):
            clean_file_path = self.schema_dir / f"{file_path}.json"
            if not clean_file_path.exists():
                clean_file_path = pathlib.Path(file_path)
        else:
            clean_file_path = file_path

        if exists is True and not clean_file_path.exists():
            raise FileNotFoundError(f"Schema file not found: {clean_file_path}")
        if exists is False and clean_file_path.exists():
            raise FileExistsError(f"Schema file already exists: {clean_file_path}")
        return clean_file_path

    def load(self, identifier: str | pathlib.Path) -> BaseSchemaVersionedModelV1:
        """Read a schema instance from a JSON file, migrating it to the current version first.

        :param identifier: Name of file or path to file containing schema data. If file_path is
            a string, checks ``self.schema_dir`` for a file whose name matches file_path. If no
            such file exists, file_path is cast to a pathlib Path.
        :return: The current-version schema instance loaded from the file, dispatched by its
            ``"type"`` field.
        """
        file_path = self._resolve_file_path(identifier, exists=True)
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        migrated = migrate_data_to_latest(
            data=data,
            schema_name=data["type"],
            schema_version=data.get("schema_version", 1),
        )
        return schema_registry.build_instance(migrated)

    def write(self, identifier: str | pathlib.Path, schema: BaseSchemaVersionedModelV1) -> None:
        """Write a schema instance to a JSON file.

        :param identifier: Path to file where the schema data will be written.
        :param schema: Schema instance to write to file.
        """
        file_path = pathlib.Path(identifier)
        with file_path.open("w", encoding="utf-8") as f:
            f.write(schema.model_dump_json(indent=2))


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
    schema_io = SchemaIO(schema_dir=labware_dir)
    return cast(tc.LabwareDescription, schema_io.load(identifier))


def generate_id() -> str:
    """Generate a UUIDv4 and pack as a URL-safe base64 encoded string.

    :return: generated string. This string contains 122 bits of entropy, equivalent to UUIDv4
    """
    return base64.urlsafe_b64encode(uuid.uuid4().bytes)[:-2].decode("utf-8")


def well_address_to_index(well_address: str, row_count: int = 8, column_count: int = 12) -> int:
    """Convert a well address (e.g. "A1") to a zero-based index.

    :param well_address: Well address in the format 'A1'
    :param row_count: Number of rows in the plate. Defaults to 8.
    :param column_count: Number of columns in the plate. Defaults to 12.

    :return: Zero-based index corresponding to the well address. Defaults provide values from 0-95.
    """
    try:
        row_letter = well_address[0].upper()
    except AttributeError as err:
        raise TypeError(f"Expected well_address to be a string, got {type(well_address)}") from err
    column_number = int(well_address[1:])
    row_index = ord(row_letter) - ord("A")
    column_index = column_number - 1
    if row_index < 0 or row_index >= row_count:
        raise ValueError(f"Invalid row letter {row_letter} for row count {row_count}")
    if column_index < 0 or column_index >= column_count:
        raise ValueError(f"Invalid column number {column_number} for column count {column_count}")
    return row_index * column_count + column_index


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


def matrix_from_euler_angles(z_angle: float, y_angle: float = 0.0, x_angle: float = 0.0) -> Matrix:
    """Create a rotation object from an euler angle sequence.

    :param z_angle: Rotation around the z-axis in radians.
    :param y_angle: Rotation around the y-axis in radians.
    :param x_angle: Rotation around the x-axis in radians.

    :return: A rotation object representing the specified euler angles.
    """
    rot = Rotation.from_euler(
        seq=SCIPY_SEQ, angles=np.array([z_angle, y_angle, x_angle]), degrees=SCIPY_DEGREES
    )
    rmat = rot.as_matrix()
    tf = np.eye(4)
    tf[:3, :3] = rmat
    return tf.tolist()


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
    errs: list[Exception] = []
    for name, value in (
        ("x", x),
        ("y", y),
        ("z", z),
        ("a", a),
        ("b", b),
        ("c", c),
    ):
        if value is not None and not isinstance(value, tc.ValueWithUnits):
            errs.append(
                TypeError(f"Expected {name} to be of type ValueWithUnits, got {type(value)}")
            )

    if errs:
        raise ExceptionGroup(f"{len(errs)} invalid parameter types in create_transform", errs)

    if x is None:
        x = tc.ValueWithUnits(magnitude=0.0, units="m")
    if y is None:
        y = tc.ValueWithUnits(magnitude=0.0, units="m")
    if z is None:
        z = tc.ValueWithUnits(magnitude=0.0, units="m")
    if a is None:
        a = tc.ValueWithUnits(magnitude=0.0, units="radians")
    if b is None:
        b = tc.ValueWithUnits(magnitude=0.0, units="radians")
    if c is None:
        c = tc.ValueWithUnits(magnitude=0.0, units="radians")

    matrix = matrix_from_euler_angles(
        z_angle=a.to("rad").magnitude,
        y_angle=b.to("rad").magnitude,
        x_angle=c.to("rad").magnitude,
    )
    matrix[0][3] = x.to("m").magnitude
    matrix[1][3] = y.to("m").magnitude
    matrix[2][3] = z.to("m").magnitude
    return matrix


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
    tags: tc.Tags | None = None,
    named_tags: tc.NamedTags | None = None,
    row_count: int = 8,
    column_count: int = 12,
    row_pitch: float = 0.009,
    column_pitch: float = 0.009,
    has_lid: bool = False,
    supports_lid: bool = False,
) -> tc.WellPlateDescriptor:
    """tc.WellPlateDescriptor constructor with nice defaults.

    :param tags: List of tags associated with the well plate. Defaults to an empty list.
    :param named_tags: Dictionary of named tags associated with the well plate. Defaults to an empty dictionary.
    :param row_count: Number of rows in the well plate. Defaults to 8.
    :param column_count: Number of columns in the well plate. Defaults to 12.
    :param row_pitch: Pitch between rows in meters. Defaults to 0.009 m.
    :param column_pitch: Pitch between columns in meters. Defaults to 0.009 m.
    :param has_lid: Whether the well plate has a lid. Defaults to False.
    :param supports_lid: Whether the well plate supports a lid. Defaults to False.

    :return: tc.WellPlateDescriptor constructed with the specified parameters.
    :raise ValueError: If has_lid is True and supports_lid is False, as this is an invalid configuration.
    """
    if has_lid and not supports_lid:
        raise ValueError(
            "Invalid configuration: has_lid is True but supports_lid is False. A well plate cannot have a lid if it does not support one."
        )
    tags = [] if tags is None else tags
    named_tags = {} if named_tags is None else named_tags
    grid_descriptor = tc.GridDescriptor(
        row_count=row_count,
        column_count=column_count,
        row_pitch=m(row_pitch),
        column_pitch=m(column_pitch),
    )
    return tc.WellPlateDescriptor(
        tags=tags,
        named_tags=named_tags,
        grid=grid_descriptor,
        liddability=tc.LiddabilityDescriptor(
            supports_lid=supports_lid, lid=tc.LidDescriptor() if has_lid else None
        ),
    )


def describe_pipette_tip_box(
    tags: tc.Tags | None = None,
    named_tags: tc.NamedTags | None = None,
    row_count: int = 8,
    column_count: int = 12,
    row_pitch: float = 0.009,
    column_pitch: float = 0.009,
    pipette_tip_layout: tc.PipetteTipLayout | None = None,
) -> tc.PipetteTipBoxDescriptor:
    """tc.PipetteTipBoxDescriptor constructor with nice defaults.

    :param tags: List of tags associated with the pipette tip box. Defaults to an empty list.
    :param named_tags: Dictionary of named tags associated with the pipette tip box. Defaults to an empty dictionary.
    :param row_count: Number of rows in the pipette tip box. Defaults to 8.
    :param column_count: Number of columns in the pipette tip box. Defaults to 12.
    :param row_pitch: Pitch between rows in meters. Defaults to 0.009 m.
    :param column_pitch: Pitch between columns in meters. Defaults to 0.009 m.
    :param pipette_tip_layout: Layout of pipette tips in the box. Defaults to a full box (i.e. all positions filled with tips).

    :return: tc.PipetteTipBoxDescriptor constructed with the specified parameters.
    """
    tags = [] if tags is None else tags
    named_tags = {} if named_tags is None else named_tags
    pipette_tip_layout = pipette_tip_layout or tc.PipetteTipLayout.full()
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
        pipette_tip_layout=pipette_tip_layout,
    )


def describe_pipette_tip_group(
    row_count: int = 1,
    column_count: int = 1,
    tags: tc.Tags | None = None,
    named_tags: tc.NamedTags | None = None,
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


def format_seconds(seconds: float) -> str:
    """Format a duration in seconds to human-readable format"""
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86_400)
    hours, seconds = divmod(seconds, 3_600)
    minutes, seconds = divmod(seconds, 60)
    time_without_days = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    if days == 0:
        return time_without_days
    elif days == 1:
        return f"{days:02d} day, {time_without_days}"
    else:
        return f"{days:02d} days, {time_without_days}"


describe_pipette_tip_1x1 = functools.partial(
    describe_pipette_tip_group, row_count=1, column_count=1
)
describe_pipette_tip_1x1.__name__ = "describe_pipette_tip_1x1"  # type: ignore [attr-defined]
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
describe_pipette_tip_1x8.__name__ = "describe_pipette_tip_1x8"  # type: ignore [attr-defined]
describe_pipette_tip_1x8.__doc__ = (
    "tc.PipetteTipGroup constructor for an 8-channel pipette tip group.\n\n"
    "param id: Unique identifier for the pipette tip group. Defaults to generate_id().\n"
    "param tags: List of tags applied to the pipette tip. Defaults to an empty list.\n"
    "param named_tags: Dictionary of named tags applied to the pipette tip. Defaults to an empty dictionary.\n\n"
    "return: tc.PipetteTipGroup with 1 row and 8 columns."
)
