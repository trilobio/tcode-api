"""Pydantic BaseModel definitions of TCode API."""

from enum import Enum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field


class _BaseModelStrict(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


class _BaseModelWithId(_BaseModelStrict):
    id: str


class ValueWithUnits(_BaseModelStrict):
    type: Literal["ValueWithUnits"] = "ValueWithUnits"
    magnitude: float
    units: str

    def __hash__(self):
        # TODO (connor): Mia mentioned that this can produce collisions, fix.
        return hash(self.magnitude) ^ hash(self.units)

    def __str__(self):
        return f"{self.magnitude} {self.units}"


class _EnumWithDisplayName(Enum):
    """Base class for Enum with display_name attribute."""

    def __init__(self, value: int, display_name: str):
        self._value_ = value
        self.display_name = display_name

    @classmethod
    def from_value(cls, value: str | int) -> Self:
        if isinstance(value, int):
            for member in cls:
                if member.value == value:
                    return member

        elif isinstance(value, str):
            for member in cls:
                if member.name == value.upper() or member.display_name == value:
                    return member

        else:
            raise TypeError(f"Invalid value type: {type(value)}")

        raise ValueError("Invalid value: {value}")


Matrix = list[list[float]]


def identity_transform_factory() -> Matrix:
    """Create new list of lists representing an identity matrix."""
    return [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def verify_positive_nonzero_int(value: int) -> int:
    """Validator to ensure the value is a positive non-zero integer."""
    if value <= 0:
        raise ValueError(f"Value must be > 0, not {value}")

    return value


class _Location(_BaseModelStrict):
    """Base schema shared by all locations in the Location discriminated union."""

    type: str


class LocationAsLabwareHolder(_Location):
    """Location specified by a labware holder's name."""

    type: Literal["LocationAsLabwareHolder"] = "LocationAsLabwareHolder"
    robot_id: str
    labware_holder_name: str


class LocationAsLabwareIndex(_Location):
    """Location specified by a tuple of labware id and labware location index."""

    type: Literal["LocationAsLabwareIndex"] = "LocationAsLabwareIndex"
    labware_id: str
    location_index: int


class LocationAsNodeId(_Location):
    """Location specified by a node ID in the fleet's transform tree."""

    type: Literal["LocationAsNodeId"] = "LocationAsNodeId"
    node_id: str


class LocationRelativeToLabware(_Location):
    """Location specified by a transformation matrix relative to a labware's base node."""

    type: Literal["LocationRelativeToLabware"] = "LocationRelativeToLabware"
    labware_id: str
    matrix: Matrix  # 4x4 transformation matrix


class LocationRelativeToWorld(_Location):
    """Location specified by a transformation matrix relative to the fleet's root node."""

    type: Literal["LocationRelativeToWorld"] = "LocationRelativeToWorld"
    matrix: Matrix  # 4x4 transformation matrix


Location = Annotated[
    LocationAsLabwareHolder
    | LocationAsLabwareIndex
    | LocationAsNodeId
    | LocationRelativeToLabware
    | LocationRelativeToWorld,
    Field(discriminator="type"),
]


class PipetteTipGroupDescriptor(_BaseModelStrict):
    """Grid layout of pipette tips."""

    type: Literal["PipetteTipGroupDescriptor"] = "PipetteTipGroupDescriptor"

    row_count: Annotated[int, verify_positive_nonzero_int]
    column_count: Annotated[int, verify_positive_nonzero_int]
    pipette_tip_tags: list[str] = Field(default_factory=list)
    pipette_tip_named_tags: dict[str, str] = Field(default_factory=dict)


# Tool schemas


class _ToolBaseDescriptor(_BaseModelStrict):
    """Base schema shared by all tools in the TOOL discriminated union."""

    ...


class ProbeDescriptor(_ToolBaseDescriptor):
    type: Literal["ProbeDescriptor"] = "ProbeDescriptor"


class GripperDescriptor(_ToolBaseDescriptor):
    type: Literal["GripperDescriptor"] = "GripperDescriptor"


class _PipetteBaseDescriptor(_ToolBaseDescriptor):
    min_volume: ValueWithUnits | None = Field(default=None)
    max_volume: ValueWithUnits | None = Field(default=None)
    max_speed: ValueWithUnits | None = Field(default=None)


class SingleChannelPipetteDescriptor(_PipetteBaseDescriptor):
    type: Literal["SingleChannelPipetteDescriptor"] = "SingleChannelPipetteDescriptor"


class EightChannelPipetteDescriptor(_PipetteBaseDescriptor):
    type: Literal["EightChannelPipetteDescriptor"] = "EightChannelPipetteDescriptor"


# Define the Tool discriminated union
ToolDescriptor = Annotated[
    SingleChannelPipetteDescriptor
    | EightChannelPipetteDescriptor
    | ProbeDescriptor
    | GripperDescriptor,
    Field(discriminator="type"),
]

PipetteDescriptor = Annotated[
    SingleChannelPipetteDescriptor | EightChannelPipetteDescriptor,
    Field(discriminator="type"),
]


class LabwareHolderDescriptor(BaseModel):
    """Descriptor for an entity that can hold labware."""

    type: Literal["LabwareHolderDescriptor"] = "LabwareHolderDescriptor"


class ToolHolderDescriptor(BaseModel):
    """Descriptor for an entity that can hold tools."""

    type: Literal["ToolHolderDescriptor"] = "ToolHolderDescriptor"


class RobotDescriptor(BaseModel):
    """Descriptor for a robot in the fleet."""

    type: Literal["RobotDescriptor"] = "RobotDescriptor"
    serial_number: str | None = None
    tools: dict[str, ToolDescriptor] = Field(default_factory=dict)
    tool_holders: dict[str, ToolHolderDescriptor] = Field(default_factory=dict)
    labware_holders: dict[str, LabwareHolderDescriptor] = Field(default_factory=dict)


class PathType(int, Enum):
    """Enumeration of robot path types.

    DIRECT: robot moves to the target location directly in jointspace.
    SAFE: robot moves to the target location via a safe path.
    SHORTCUT: robot uses DIRECT if it is close to the target, othserwise SAFE.
    """

    DIRECT = 1
    SAFE = 2
    SHORTCUT = 3


class GraspType(str, Enum):
    """Enumeration of robot gripper grasp types.

    PINCH: robot actively pinches the labware from the sides.
    LIFT: robot passively lifts the labware from the bottom.
    """

    UNSPECIFIED = "UNSPECIFIED"
    LIFT = "LIFT"
    PINCH = "PINCH"


class TrajectoryType(int, Enum):
    """Enumeration of trajectory types.

    JOINT_SQUARE: robot moves in joint space with square motor profiles.
    JOINT_TRAPEZOIDAL: robot moves in joint space with trapezoidal motor profiles.
    LINEAR: robot moves in cartesian space with non-uniform motor profiles.
    """

    JOINT_SQUARE = 1
    JOINT_TRAPEZOIDAL = 2


### Well Shape Descriptors ###
class CircleDescriptor(BaseModel):
    """Discriptor of a circle."""

    type: Literal["CircleDescriptor"] = "CircleDescriptor"
    diameter: ValueWithUnits | None = None


class AxisAlignedRectangleDescriptor(BaseModel):
    """Descriptor of an axis-aligned rectangle."""

    type: Literal["AxisAlignedRectangleDescriptor"] = "AxisAlignedRectangleDescriptor"
    width: ValueWithUnits | None = None
    length: ValueWithUnits | None = None


WellShapeDescriptor = Annotated[
    CircleDescriptor | AxisAlignedRectangleDescriptor,
    Field(discriminator="type"),
]


### Well Bottom Profile Descriptors ###
class _BaseWellBottomProfileDescriptor(BaseModel):
    """Base descriptor for well bottom profiles."""

    type: str


class FlatBottomDescriptor(_BaseWellBottomProfileDescriptor):
    """Descriptor for a flat bottom well."""

    type: Literal["FlatBottomDescriptor"] = "FlatBottomDescriptor"


class RoundBottomDescriptor(_BaseWellBottomProfileDescriptor):
    """Descriptor for a round bottom well."""

    type: Literal["RoundBottomDescriptor"] = "RoundBottomDescriptor"
    # radius: the radius is inferred from the well's diameter


class VBottomDescriptor(_BaseWellBottomProfileDescriptor):
    """Descriptor for a V-bottom well (think trough)."""

    type: Literal["VBottomDescriptor"] = "VBottomDescriptor"
    direction: Literal["Width-wide", "Length-wide"] | None = None
    offset: ValueWithUnits | None = None


class ConicalBottomDescriptor(_BaseWellBottomProfileDescriptor):
    """Descriptor for a conical bottom well."""

    type: Literal["ConicalBottomDescriptor"] = "ConicalBottomDescriptor"
    # angle: assumed to come to a point at the bottom of the well
    offset: ValueWithUnits | None = None


WellBottomShapeDescriptor = Annotated[
    FlatBottomDescriptor | RoundBottomDescriptor | VBottomDescriptor,
    Field(discriminator="type"),
]


class GridDescriptor(_BaseModelStrict):
    """Descriptor for a grid layout."""

    type: Literal["GridDescriptor"] = "GridDescriptor"
    row_count: int | None = None
    column_count: int | None = None
    row_pitch: ValueWithUnits | None = None
    column_pitch: ValueWithUnits | None = None
    row_offset: ValueWithUnits | None = None
    column_offset: ValueWithUnits | None = None


class WellDescriptor(_BaseModelStrict):
    """Descriptor for a well in a labware."""

    type: Literal["WellDescriptor"] = "WellDescriptor"
    depth: ValueWithUnits | None = None
    shape: WellShapeDescriptor | None = None
    bottom_shape: WellBottomShapeDescriptor | None = None
    min_volume: ValueWithUnits | None = None
    max_volume: ValueWithUnits | None = None
    well_tags: list[str] = Field(default_factory=list)
    well_named_tags: dict[str, str] = Field(default_factory=dict)


# Labware Descriptors
# These schemas are NOT intended to fully represent a labware, but instead to
# contain a minimal representation of required features for a labware.
class _LabwareBaseDescriptor(_BaseModelStrict):
    """Base schema shared by all labware in the Labware discriminated union."""

    tags: list[str] = Field(default_factory=list)
    named_tags: dict[str, str] = Field(default_factory=dict)


class LidDescriptor(_LabwareBaseDescriptor):
    """A descriptor of the minimal features required by protocol-specified plate lid."""

    type: Literal["LidDescriptor"] = "LidDescriptor"


class WellPlateDescriptor(_LabwareBaseDescriptor):
    """A descriptor of the minimal features required by protocol-specified well plate."""

    type: Literal["WellPlateDescriptor"] = "WellPlateDescriptor"
    grid_descriptor: GridDescriptor | None = None
    well_descriptor: WellDescriptor | None = None

    # Lid parameters
    has_lid: bool = False
    lid_offset: ValueWithUnits | None = None
    lid_descriptor: LidDescriptor | None = None


class PipetteTipRackDescriptor(_LabwareBaseDescriptor):
    """A descriptor of the minimal features required by protocol-specified pipette tip rack."""

    type: Literal["PipetteTipRackDescriptor"] = "PipetteTipRackDescriptor"
    grid_descriptor: GridDescriptor | None = None
    full: bool | None = None


class TrashDescriptor(_LabwareBaseDescriptor):
    """A descriptor of the minimal features required by protocol-specified waste disposal container."""

    type: Literal["TrashDescriptor"] = "TrashDescriptor"
    depth: ValueWithUnits | None = None


LabwareDescriptor = Annotated[
    WellPlateDescriptor | PipetteTipRackDescriptor | TrashDescriptor | LidDescriptor,
    Field(discriminator="type"),
]


# Labware Descriptions
# These schemas are intended to be identical to Descriptors, but with no optional attributes.
class _LabwareBaseDescription(_BaseModelStrict):
    """Base schema shared by all labware in the LabwareDescription discriminated union."""

    type: str
    tags: list[str] = Field(default_factory=list)
    named_tags: dict[str, str] = Field(default_factory=dict)
    height: ValueWithUnits


class LidDescription(_LabwareBaseDescription):
    """A full description of a plate lid."""

    type: Literal["LidDescription"] = "LidDescription"


class GridDescription(_BaseModelStrict):
    """A full description of a grid layout."""

    type: Literal["GridDescription"] = "GridDescription"

    row_count: int
    column_count: int
    row_pitch: ValueWithUnits
    column_pitch: ValueWithUnits
    row_offset: ValueWithUnits
    column_offset: ValueWithUnits


class WellDescription(_BaseModelStrict):
    """A full description of a well in a labware."""

    type: Literal["WellDescription"] = "WellDescription"
    tags: list[str] = Field(default_factory=list)
    named_tags: dict[str, str] = Field(default_factory=dict)

    depth: ValueWithUnits
    shape: WellShapeDescriptor
    bottom_shape: WellBottomShapeDescriptor
    min_volume: ValueWithUnits
    max_volume: ValueWithUnits


class WellPlateDescription(_LabwareBaseDescription):
    """A full description of a well plate."""

    type: Literal["WellPlateDescription"] = "WellPlateDescription"

    grid_description: GridDescription
    well_description: WellDescription

    # Lid parameters
    has_lid: bool
    lid_offset: ValueWithUnits | None
    lid_description: LidDescription | None


class PipetteTipDescription(_LabwareBaseDescription):
    """A full description of a pipette tip."""

    type: Literal["PipetteTipDescription"] = "PipetteTipDescription"
    flange_height: ValueWithUnits


class PipetteTipRackDescription(_LabwareBaseDescription):
    """A full description of a pipette tip rack."""

    type: Literal["PipetteTipRackDescription"] = "PipetteTipRackDescription"

    grid_description: GridDescription
    full: bool
    pipette_tip_description: PipetteTipDescription


class TrashDescription(_LabwareBaseDescriptor):
    """A full description of a waste disposal container."""

    type: Literal["TrashDescription"] = "TrashDescription"
    depth: ValueWithUnits


LabwareDescription = Annotated[
    WellPlateDescription
    | PipetteTipRackDescription
    | TrashDescription
    | LidDescription,
    Field(discriminator="type"),
]


# TCode command schemas
class _TCodeBase(_BaseModelStrict):
    """Base schema shared by all TCode commands in the TCODE discriminated union."""

    ...


class _RobotSpecificTCodeBase(_TCodeBase):
    """Base schema shared by all TCode commands that are specific to a robot.

    This is used to ensure that the command is only executed on the robot with the specified id.
    """

    robot_id: str


class ADD_LABWARE(_TCodeBase):
    type: Literal["ADD_LABWARE"] = "ADD_LABWARE"
    id: str
    descriptor: LabwareDescriptor


class ADD_ROBOT(_TCodeBase):
    type: Literal["ADD_ROBOT"] = "ADD_ROBOT"
    id: str
    descriptor: RobotDescriptor


class ADD_PIPETTE_TIP_GROUP(_TCodeBase):
    type: Literal["ADD_PIPETTE_TIP_GROUP"] = "ADD_PIPETTE_TIP_GROUP"
    id: str
    descriptor: PipetteTipGroupDescriptor


class ADD_TOOL(_TCodeBase):
    type: Literal["ADD_TOOL"] = "ADD_TOOL"
    id: str
    descriptor: ToolDescriptor
    robot_id: str


class ASPIRATE(_RobotSpecificTCodeBase):
    type: Literal["ASPIRATE"] = "ASPIRATE"
    volume: ValueWithUnits
    speed: ValueWithUnits


class CALIBRATE_LABWARE_HEIGHT(_RobotSpecificTCodeBase):
    """TCode command to use the currently held tool to tune the height of a target labware by probing.

    :param location: The location attribute specifes which labware and where on the labware to probe.
        Unlike other location-based commands (ex. :class: MOVE_TO_LOCATION), :class: CALIBRATE_LABWARE_HEIGHT
        only supports locations that hold references to a labware.
    :param persistent: When raised, all labware of the same type and brand will be modified. This
        calibration DOES NOT APPLY
        If not raised, only the current in-place transform is applied. Restarting the tcode
        server will reset the calibration.
    """

    type: Literal["CALIBRATE_LABWARE_HEIGHT"] = "CALIBRATE_LABWARE_HEIGHT"
    location: LocationAsLabwareIndex | LocationRelativeToLabware
    persistent: bool


class CALIBRATE_LABWARE_WELL_DEPTH(_RobotSpecificTCodeBase):
    """TCode command to use the currently held tool to tune the depth of a target labware's well by probing.

    An example TCode snippet to calibrate using a pipette tip is here:
    ```
    RETRIEVE_TOOL(id=...)
    RETRIEVE_PIPETTE_TIP_GROUP(id=...)
    CALIBRATE_PIPETTE_TIP_LENGTH()
    CALIBRATE_LABWARE_WELL_DEPTH(location=LocationAsLabwareIndex(labware_id=..., location_index=...))
    ```

    :param location: The location attribute specifes which labware and where on the labware to probe.
        Unlike other location-based commands (ex. :class: MOVE_TO_LOCATION), :class: CALIBRATE_LABWARE_WELL_DEPTH
        only supports locations that hold references to a labware.
    :param modify_all_wells: This flag indicates whether only the probed well's depth should be modified,
        or if the depths of all of the wells in the labware should be modified.
        Defaults to modifying all of the wells.
    :param persistent: When raised, all labware of the same type and brand will be modified. This
        calibration DOES NOT APPLY
        If not raised, only the current in-place transform is applied. Restarting the tcode
        server will reset the calibration.
    """

    type: Literal["CALIBRATE_LABWARE_WELL_DEPTH"] = "CALIBRATE_LABWARE_WELL_DEPTH"
    location: LocationAsLabwareIndex | LocationRelativeToLabware
    modify_all_wells: bool = True
    persistent: bool


class CALIBRATE_TOOL_FOR_PROBING(_RobotSpecificTCodeBase):
    """TCode command to calibrate the tool for probing.

    If a bare tool is held, the tool's transform will be calibrated. If a pipette tip is held, the
    pipette tip's relationship to the tool will be calibrated.

    :param z_only: When raised, tool is only calibrated for z-axis probing. If not raised,
        tool is calibrated for x, y, and z.
    :param persistent: When raised, the behavior is dependent on the tool mounted.
        If a bare tool is mounted, the transform is saved to the tool's configuration.
        If a pipette tip is mounted, the transform is applied to all pipette tips of that brand.
        If not raised, only the currently in-place transform is applied. Restarting the tcode
        server will reset the calibration.
    """

    type: Literal["CALIBRATE_TOOL_FOR_PROBING"] = "CALIBRATE_TOOL_FOR_PROBING"
    z_only: bool
    persistent: bool = False


class CREATE_LABWARE(_RobotSpecificTCodeBase):
    """TCode command to create a new labware on the deck of a robot in the fleet.

    :param robot_id: The ID of the robot on which to create the labware.
    :param description: The labware descriptor that describes the labware to be created.
        Must be fully filled out, UNLIKE typical labware descriptors (which may have unprovided fields).
    :param deck_slot_name: The name of the deck slot where the labware will be created on the target robot.
    """

    type: Literal["CREATE_LABWARE"] = "CREATE_LABWARE"
    description: LabwareDescription
    deck_slot_name: str


class COMMENT(_TCodeBase):
    type: Literal["COMMENT"] = "COMMENT"
    text: str


class DELETE_LABWARE(_RobotSpecificTCodeBase):
    """TCode command to delete a labware from the fleet.

    :param labware_id: The ID of the labware to be deleted.
    """

    type: Literal["DELETE_LABWARE"] = "DELETE_LABWARE"
    labware_id: str


class DISCARD_PIPETTE_TIP_GROUP(_RobotSpecificTCodeBase):
    type: Literal["DISCARD_PIPETTE_TIP_GROUP"] = "DISCARD_PIPETTE_TIP_GROUP"


class DISPENSE(_RobotSpecificTCodeBase):
    type: Literal["DISPENSE"] = "DISPENSE"
    volume: ValueWithUnits
    speed: ValueWithUnits


class MOVE_TO_LOCATION(_RobotSpecificTCodeBase):
    type: Literal["MOVE_TO_LOCATION"] = "MOVE_TO_LOCATION"
    location: Location
    location_offset: Matrix = Field(default_factory=identity_transform_factory)
    flange: Location | None = None
    flange_offset: Matrix = Field(default_factory=identity_transform_factory)
    path_type: int | None = None  # PathType | None = None
    trajectory_type: int | None = None  # TrajectoryType | None = None


class PAUSE(_TCodeBase):
    type: Literal["PAUSE"] = "PAUSE"


class PICK_UP_LABWARE(_RobotSpecificTCodeBase):
    type: Literal["PICK_UP_LABWARE"] = "PICK_UP_LABWARE"
    labware_id: str
    grasp_type: str = GraspType.UNSPECIFIED.value


class PUT_DOWN_LABWARE(_RobotSpecificTCodeBase):
    type: Literal["PUT_DOWN_LABWARE"] = "PUT_DOWN_LABWARE"
    location: Location


class REMOVE_LABWARE_LID(_RobotSpecificTCodeBase):
    type: Literal["REMOVE_LABWARE_LID"] = "REMOVE_LABWARE_LID"
    labware_id: str
    storage_location: Location | None = None


class REPLACE_LABWARE_LID(_RobotSpecificTCodeBase):
    type: Literal["REPLACE_LABWARE_LID"] = "REPLACE_LABWARE_LID"
    labware_id: str
    lid_id: str | None = None


class PICK_UP_PIPETTE_TIP(_RobotSpecificTCodeBase):
    type: Literal["PICK_UP_PIPETTE_TIP"] = "PICK_UP_PIPETTE_TIP"
    location: Location


class PUT_DOWN_PIPETTE_TIP(_RobotSpecificTCodeBase):
    type: Literal["PUT_DOWN_PIPETTE_TIP"] = "PUT_DOWN_PIPETTE_TIP"
    location: Location


class RETRIEVE_PIPETTE_TIP_GROUP(_RobotSpecificTCodeBase):
    type: Literal["RETRIEVE_PIPETTE_TIP_GROUP"] = "RETRIEVE_PIPETTE_TIP_GROUP"
    id: str


class RETRIEVE_TOOL(_RobotSpecificTCodeBase):
    type: Literal["RETRIEVE_TOOL"] = "RETRIEVE_TOOL"
    id: str


class RETURN_PIPETTE_TIP_GROUP(_RobotSpecificTCodeBase):
    type: Literal["RETURN_PIPETTE_TIP_GROUP"] = "RETURN_PIPETTE_TIP_GROUP"


class RETURN_TOOL(_RobotSpecificTCodeBase):
    type: Literal["RETURN_TOOL"] = "RETURN_TOOL"


class WAIT(_RobotSpecificTCodeBase):
    type: Literal["WAIT"] = "WAIT"
    duration: ValueWithUnits


TCode = Annotated[
    ASPIRATE
    | ADD_LABWARE
    | ADD_PIPETTE_TIP_GROUP
    | ADD_ROBOT
    | ADD_TOOL
    | CALIBRATE_LABWARE_WELL_DEPTH
    | CALIBRATE_LABWARE_HEIGHT
    | CALIBRATE_TOOL_FOR_PROBING
    | COMMENT
    | CREATE_LABWARE
    | DELETE_LABWARE
    | DISCARD_PIPETTE_TIP_GROUP
    | DISPENSE
    | MOVE_TO_LOCATION
    | PAUSE
    | PICK_UP_LABWARE
    | PICK_UP_PIPETTE_TIP
    | PUT_DOWN_LABWARE
    | PUT_DOWN_PIPETTE_TIP
    | REMOVE_LABWARE_LID
    | REPLACE_LABWARE_LID
    | RETRIEVE_PIPETTE_TIP_GROUP
    | RETRIEVE_TOOL
    | RETURN_PIPETTE_TIP_GROUP
    | RETURN_TOOL
    | WAIT,
    Field(discriminator="type"),
]


# Top-level component schemas


class Fleet(_BaseModelStrict):
    robots: dict[str, RobotDescriptor] = Field(default_factory=dict)
    labware: dict[str, LabwareDescriptor] = Field(default_factory=dict)


class Metadata(_BaseModelStrict):
    """TCode script metadata."""

    name: str
    timestamp: str  # ISO 8601 timestamp string
    tcode_api_version: str
    description: str | None = Field(default=None)


class TCodeScript(BaseModel):
    """Structure of a TCode script."""

    metadata: Metadata
    commands: list[TCode] = Field(default_factory=list)
