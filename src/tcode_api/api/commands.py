"""Definitions of TCode commands."""

from typing import Annotated, Literal

from pydantic import Field

from tcode_api.api.core import (
    ValueWithUnits,
    _ConfiguredBaseModel,
    identity_transform_factory,
)
from tcode_api.api.entity import GraspType, RobotDescriptor, ToolDescriptor
from tcode_api.api.labware import (
    LabwareDescription,
    LabwareDescriptor,
    PipetteTipGroupDescriptor,
)
from tcode_api.api.location import (
    Location,
    LocationAsLabwareIndex,
    LocationRelativeToLabware,
)
from tcode_api.types import Matrix


class _TCodeBase(_ConfiguredBaseModel):
    """Base schema shared by all TCode commands in the TCODE discriminated union."""

    ...


class _RobotSpecificTCodeBase(_TCodeBase):
    """Base schema shared by all TCode commands that are specific to a robot.

    This is used to ensure that the command is only executed on the robot with the specified id.
    """

    robot_id: str


class ADD_LABWARE(_TCodeBase):
    """Resolve the given descriptor to a labware on the fleet and assign it the given id."""
    type: Literal["ADD_LABWARE"] = "ADD_LABWARE"
    id: str
    descriptor: LabwareDescriptor


class ADD_ROBOT(_TCodeBase):
    """Resolve the given descriptor to a robot on the fleet and assign it the given id."""
    type: Literal["ADD_ROBOT"] = "ADD_ROBOT"
    id: str
    descriptor: RobotDescriptor


class ADD_PIPETTE_TIP_GROUP(_TCodeBase):
    """Resolve the given descriptor to a list of pipette tips on the fleet and assign it the given id."""
    type: Literal["ADD_PIPETTE_TIP_GROUP"] = "ADD_PIPETTE_TIP_GROUP"
    id: str
    descriptor: PipetteTipGroupDescriptor


class ADD_TOOL(_TCodeBase):
    """Resolve the given descriptor to a tool on the fleet and assign it the given id."""
    type: Literal["ADD_TOOL"] = "ADD_TOOL"
    id: str
    descriptor: ToolDescriptor
    robot_id: str


class ASPIRATE(_RobotSpecificTCodeBase):
    """Command the targeted robot to aspirate a given fluid volume at a given speed."""
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
    """Command the targeted robot to calibrate the currently held tool for probing.

    :note: If a bare tool is held, the tool's transform will be calibrated.
    :note: If a pipette tip is held, the pipette tip's relationship to the tool will be calibrated.

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
    """Create a new physical labware on the targeted robot's deck.

    :note: This command adds a labware to TCode's internal state; the description provided is NOT a descriptor, and is NOT resolved.
    :note: The labware will be created in the specified deck slot, and TCode will from here on assume that the slot is occupied by this labware.
    """

    type: Literal["CREATE_LABWARE"] = "CREATE_LABWARE"
    description: LabwareDescription
    deck_slot_name: str


class COMMENT(_TCodeBase):
    """A comment, included for human readability and comprehension of the TCode script."""
    type: Literal["COMMENT"] = "COMMENT"
    text: str


class DELETE_LABWARE(_RobotSpecificTCodeBase):
    """Physically remove the labware associated with the given id from the targeted robot's deck.

    :note: This labware will no longer be available to future ADD_LABWARE resolution
    :note: TCode will assume that the holder previously occupied by this labware is now empty.
    """
    type: Literal["DELETE_LABWARE"] = "DELETE_LABWARE"
    labware_id: str


class DISCARD_PIPETTE_TIP_GROUP(_RobotSpecificTCodeBase):
    """Command the targeted robot to dispose of its currently held pipette tip(s) into any accessible dry waste disposal location."""
    type: Literal["DISCARD_PIPETTE_TIP_GROUP"] = "DISCARD_PIPETTE_TIP_GROUP"


class DISPENSE(_RobotSpecificTCodeBase):
    """Command the targeted robot to dispense a given fluid volume at a given speed."""
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


class SWAP_TO_TOOL(_RobotSpecificTCodeBase):
    type: Literal["SWAP_TO_TOOL"] = "SWAP_TO_TOOL"
    id: str


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
    | SWAP_TO_TOOL
    | WAIT,
    Field(discriminator="type"),
]


class Metadata(_ConfiguredBaseModel):
    """TCode script metadata."""

    name: str
    timestamp: str  # ISO 8601 timestamp string
    tcode_api_version: str
    description: str | None = Field(default=None)


class TCodeScript(_ConfiguredBaseModel):
    """Structure of a TCode script."""

    metadata: Metadata
    commands: list[TCode] = Field(default_factory=list)
