"""TCode API definitions, implemented with Pydantic."""

import enum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from tcode_api.types import NamedTags, Tags


class _BaseModelStrict(BaseModel):
    model_config = ConfigDict(strict=True, extra="ignore")


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


Matrix = list[list[float]]


def identity_transform_factory() -> Matrix:
    """Create new list of lists representing an identity matrix."""
    return [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def verify_positive_nonzero_int(value: int) -> int:
    """Validator to ensure the value is a positive non-zero integer."""
    if value <= 0:
        raise ValueError(f"Value must be > 0, not {value}")

    return value


class WellPartType(enum.StrEnum):
    """Enumeration of well parts.

    TOP: the top part of the well, above the liquid level.
    BOTTOM: the bottom part of the well, below the liquid level.
    """

    TOP = "TOP"
    BOTTOM = "BOTTOM"


class _Location(_BaseModelStrict):
    """Base schema shared by all locations in the Location discriminated union."""

    type: str


class LocationRelativeToCurrentPosition(_Location):
    """Location specified by a transformation matrix relative to position of the robot's current control node."""

    type: Literal["LocationRelativeToCurrentPosition"] = (
        "LocationRelativeToCurrentPosition"
    )
    matrix: Matrix  # 4x4 transformation matrix


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
    well_part: str  # WellPartType


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
    | LocationRelativeToCurrentPosition
    | LocationRelativeToLabware
    | LocationRelativeToWorld,
    Field(discriminator="type"),
]


class PipetteTipGroupDescriptor(_BaseModelStrict):
    """Grid layout of pipette tips."""

    type: Literal["PipetteTipGroup"] = "PipetteTipGroup"

    row_count: Annotated[int, verify_positive_nonzero_int]
    column_count: Annotated[int, verify_positive_nonzero_int]
    pipette_tip_tags: Tags = Field(default_factory=list)
    pipette_tip_named_tags: NamedTags = Field(default_factory=dict)


# Tool schemas


class _ToolBaseDescriptor(_BaseModelStrict):
    """Base schema shared by all tools in the TOOL discriminated union."""

    ...


class ProbeDescriptor(_ToolBaseDescriptor):
    type: Literal["Probe"] = "Probe"


class GripperDescriptor(_ToolBaseDescriptor):
    type: Literal["Gripper"] = "Gripper"


class _PipetteBaseDescriptor(_ToolBaseDescriptor):
    min_volume: ValueWithUnits | None = Field(default=None)
    max_volume: ValueWithUnits | None = Field(default=None)
    max_speed: ValueWithUnits | None = Field(default=None)


class SingleChannelPipetteDescriptor(_PipetteBaseDescriptor):
    type: Literal["SingleChannelPipette"] = "SingleChannelPipette"


class EightChannelPipetteDescriptor(_PipetteBaseDescriptor):
    type: Literal["EightChannelPipette"] = "EightChannelPipette"


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

    type: Literal["LabwareHolder"] = "LabwareHolder"


class ToolHolderDescriptor(BaseModel):
    """Descriptor for an entity that can hold tools."""

    type: Literal["ToolHolder"] = "ToolHolder"


class RobotDescriptor(BaseModel):
    """Descriptor for a robot in the fleet."""

    type: Literal["Robot"] = "Robot"
    serial_number: str | None = None
    tools: dict[str, ToolDescriptor] = Field(default_factory=dict)
    tool_holders: dict[str, ToolHolderDescriptor] = Field(default_factory=dict)
    labware_holders: dict[str, LabwareHolderDescriptor] = Field(default_factory=dict)


class PathType(int, enum.Enum):
    """Enumeration of robot path types.

    DIRECT: robot moves to the target location directly in jointspace.
    SAFE: robot moves to the target location via a safe path.
    SHORTCUT: robot uses DIRECT if it is close to the target, othserwise SAFE.
    """

    DIRECT = 1
    SAFE = 2
    SHORTCUT = 3


class GraspType(str, enum.Enum):
    """Enumeration of robot gripper grasp types.

    PINCH: robot actively pinches the labware from the sides.
    LIFT: robot passively lifts the labware from the bottom.
    """

    UNSPECIFIED = "UNSPECIFIED"
    LIFT = "LIFT"
    PINCH = "PINCH"


class TrajectoryType(int, enum.Enum):
    """Enumeration of trajectory types.

    JOINT_SQUARE: robot moves in joint space with square motor profiles.
    JOINT_TRAPEZOIDAL: robot moves in joint space with trapezoidal motor profiles.
    LINEAR: robot moves in cartesian space with non-uniform motor profiles.
    """

    JOINT_SQUARE = 1
    JOINT_TRAPEZOIDAL = 2


# Well Shapes
class CircleDescription(_BaseModelStrict):
    """Description of a circle."""

    type: Literal["Circle"] = "Circle"
    diameter: ValueWithUnits


class CircleDescriptor(_BaseModelStrict):
    """CircleDescription with optional parameters."""

    type: Literal["Circle"] = "Circle"
    diameter: ValueWithUnits | None = None


class AxisAlignedRectangleDescription(_BaseModelStrict):
    """Description of an axis-aligned rectangle."""

    type: Literal["AxisAlignedRectangle"] = "AxisAlignedRectangle"
    width: ValueWithUnits
    length: ValueWithUnits


class AxisAlignedRectangleDescriptor(_BaseModelStrict):
    """AxisAlignedRectangleDescription with optional parameters."""

    type: Literal["AxisAlignedRectangle"] = "AxisAlignedRectangle"
    width: ValueWithUnits | None = None
    length: ValueWithUnits | None = None


WellShapeDescription = Annotated[
    CircleDescription | AxisAlignedRectangleDescription,
    Field(discriminator="type"),
]
WellShapeDescriptor = Annotated[
    CircleDescriptor | AxisAlignedRectangleDescriptor,
    Field(discriminator="type"),
]


# Well Bottom Profiles
class FlatBottomDescriptor(_BaseModelStrict):
    """Descriptor for a flat bottom well."""

    type: Literal["Flat"] = "Flat"


class FlatBottomDescription(FlatBottomDescriptor):
    """FlatBottomDescription with optional paramters."""


class RoundBottomDescription(_BaseModelStrict):
    """Descriptor for a round bottom well."""

    type: Literal["Round"] = "Round"
    # radius: the radius is inferred from the well's diameter


class RoundBottomDescriptor(_BaseModelStrict):
    """RoundBottomDescription with optional parameters."""

    type: Literal["Round"] = "Round"


class VBottomDescription(_BaseModelStrict):
    """Description of a V-bottom well (think trough)."""

    type: Literal["V-Shape"] = "V-Shape"
    direction: Literal["Width-wide", "Length-wide"]
    offset: ValueWithUnits


class VBottomDescriptor(_BaseModelStrict):
    """VBottomDescription with optional parameters."""

    type: Literal["V-Shape"] = "V-Shape"
    direction: Literal["Width-wide", "Length-wide"] | None = None
    offset: ValueWithUnits | None = None


class ConicalBottomDescription(_BaseModelStrict):
    """Description of a conical bottom well."""

    type: Literal["Conical"] = "Conical"
    # angle: assumed to come to a point at the bottom of the well
    offset: ValueWithUnits


class ConicalBottomDescriptor(_BaseModelStrict):
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


# Other Labware Components
class GridDescription(_BaseModelStrict):
    """Description of a grid layout."""

    type: Literal["Grid"] = "Grid"
    row_count: int
    column_count: int
    row_pitch: ValueWithUnits
    column_pitch: ValueWithUnits
    row_offset: ValueWithUnits
    column_offset: ValueWithUnits


class GridDescriptor(_BaseModelStrict):
    """GridDescription with optional parameters."""

    type: Literal["Grid"] = "Grid"
    row_count: int | None = None
    column_count: int | None = None
    row_pitch: ValueWithUnits | None = None
    column_pitch: ValueWithUnits | None = None
    row_offset: ValueWithUnits | None = None
    column_offset: ValueWithUnits | None = None


class WellDescription(_BaseModelStrict):
    """Description of a well in a labware."""

    type: Literal["Well"] = "Well"
    depth: ValueWithUnits
    shape: WellShapeDescription
    bottom_shape: WellBottomShapeDescription
    min_volume: ValueWithUnits
    max_volume: ValueWithUnits
    well_tags: Tags = Field(default_factory=list)
    well_named_tags: NamedTags = Field(default_factory=dict)


class WellDescriptor(_BaseModelStrict):
    """WellDescription with optional parameters."""

    type: Literal["Well"] = "Well"
    depth: ValueWithUnits | None = None
    shape: WellShapeDescriptor | None = None
    bottom_shape: WellBottomShapeDescriptor | None = None
    min_volume: ValueWithUnits | None = None
    max_volume: ValueWithUnits | None = None


# Non-plate labware
class PipetteTipDescription(_BaseModelStrict):
    """Description of a pipette tip."""

    type: Literal["PipetteTip"] = "PipetteTip"
    tags: Tags = Field(default_factory=list)
    named_tags: NamedTags = Field(default_factory=dict)
    has_filter: bool
    height: ValueWithUnits
    flange_height: ValueWithUnits
    max_volume: ValueWithUnits
    min_volume: ValueWithUnits


class PipetteTipDescriptor(_BaseModelStrict):
    """PipetteTipDescription with optional parameters."""

    type: Literal["PipetteTip"] = "PipetteTip"
    tags: Tags = Field(default_factory=list)
    named_tags: NamedTags = Field(default_factory=dict)
    has_filter: bool | None = None
    height: ValueWithUnits | None = None
    flange_height: ValueWithUnits | None = None
    max_volume: ValueWithUnits | None = None
    min_volume: ValueWithUnits | None = None


class TubeDescription(_BaseModelStrict):
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


class TubeDescriptor(_BaseModelStrict):
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


# Labware
class _LabwareBaseDescription(_BaseModelStrict):
    """Base schema shared by all labware in the Labware discriminated union."""

    tags: Tags = Field(default_factory=list)
    named_tags: NamedTags = Field(default_factory=dict)
    length: ValueWithUnits
    width: ValueWithUnits
    height: ValueWithUnits


class _LabwareBaseDescriptor(_BaseModelStrict):
    """Base schema shared by all labware descriptors in the LabwareDescriptor discriminated union."""

    tags: Tags = Field(default_factory=list)
    named_tags: NamedTags = Field(default_factory=dict)
    length: ValueWithUnits | None = None
    width: ValueWithUnits | None = None
    height: ValueWithUnits | None = None


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
    depth: ValueWithUnits


class TrashDescriptor(_LabwareBaseDescriptor):
    """TrashDescription with optional parameters."""

    type: Literal["Trash"] = "Trash"
    depth: ValueWithUnits | None = None


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


class MOVE_TO_JOINT_POSE(_RobotSpecificTCodeBase):
    type: Literal["MOVE_TO_JOINT_POSE"] = "MOVE_TO_JOINT_POSE"
    joint_positions: list[ValueWithUnits]
    relative: bool


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
    | MOVE_TO_JOINT_POSE
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


class Metadata(_BaseModelStrict):
    """TCode script metadata."""

    name: str
    timestamp: str  # ISO 8601 timestamp string
    tcode_api_version: str
    description: str | None = Field(default=None)


class TCodeScript(_BaseModelStrict):
    """Structure of a TCode script."""

    metadata: Metadata
    commands: list[TCode] = Field(default_factory=list)
