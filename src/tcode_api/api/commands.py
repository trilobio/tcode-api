"""TCode command model, implemented in pydantic."""

from __future__ import annotations

import datetime
import importlib.metadata
import logging
from typing import Annotated, Literal, TextIO

from pydantic import BaseModel, Field

from tcode_api.api.core import ValueWithUnits, _ConfiguredBaseModel
from tcode_api.api.entity import GraspType, RobotDescriptor, ToolDescriptor
from tcode_api.api.labware import (
    LabwareDescription,
    LabwareDescriptor,
    PipetteTipGroupDescriptor,
)
from tcode_api.api.labware_holder import LabwareHolder
from tcode_api.api.location import (
    Location,
    LocationAsLabwareIndex,
    LocationRelativeToLabware,
)
from tcode_api.types import Matrix

_logger = logging.getLogger(__name__)


class _TCodeBase(_ConfiguredBaseModel):
    """Base schema shared by all TCode commands in the TCODE discriminated union.

    :param type: Discriminator field, used to determine the specific command type.

    :raises ValidatorError: ``ValidatorErrorCode.INTERNAL_ERROR`` if any unexpected error occurs
        during validation. If this occurs, file an issue on
        https://github.com/trilobio/tcode-api/issues.
    """

    type: str


class _RobotSpecificTCodeBase(_TCodeBase):
    """Base schema shared by all TCode commands that are specific to a robot.

    This is used to ensure that the command is only executed on the robot with the specified id.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: Identifier of the robot targeted by this command
    """

    robot_id: str


class ADD_LABWARE(_TCodeBase):
    """Find a matching labware on the fleet and assign it the given id.

    :param type: see :class: ``_TCodeBase``
    :param id: Identifier to assign to the resolved labware. This id is used in subsequent commands
        to reference this labware.
    :param descriptor: Minimal descriptor of the desired labware; resolved on the fleet.
    :param lid_id: Optional identifier of a lid to associate with the labware. If provided,
        the labware descriptor must indicate that the labware has a lid.

    :raises ValidatorError: ``ValidatorErrorCode.ID_EXISTS`` if ``id`` is already registered to
        a labware.
    """

    type: Literal["ADD_LABWARE"] = "ADD_LABWARE"
    id: str
    descriptor: LabwareDescriptor
    lid_id: str | None = None


class ADD_PIPETTE_TIP_GROUP(_TCodeBase):
    """Find a matching group of pipette tips on the fleet and assign it the given id.

    :param type: see :class: ``_TCodeBase``
    :param id: Identifier to assign to the resolved pipette tip group. This id is used in subsequent
        commands to reference this pipette tip group.
    :param descriptor: Minimal descriptor of the desired pipette tip group; resolved on the fleet.

    :raises ValidatorError: ``ValidatorErrorCode.ID_EXISTS`` if ``id`` is already registered to
        a pipette tip group.
    """

    type: Literal["ADD_PIPETTE_TIP_GROUP"] = "ADD_PIPETTE_TIP_GROUP"
    id: str
    descriptor: PipetteTipGroupDescriptor


class ADD_ROBOT(_TCodeBase):
    """Find a matching robot on the fleet and assign it the given id.

    :param type: see :class: ``_TCodeBase``
    :param id: Identifier to assign to the resolved robot. This id is used in subsequent commands
        to reference this robot.
    :param descriptor: Minimal descriptor of the desired robot; resolved on the fleet.

    :raises ValidatorError: ``ValidatorErrorCode.ID_EXISTS`` if ``id`` is already registered to
        a robot.
    """

    type: Literal["ADD_ROBOT"] = "ADD_ROBOT"
    id: str
    descriptor: RobotDescriptor


class ADD_TOOL(_TCodeBase):
    """Find a matching tool on the fleet and assign it the given id.

    :note: Doesn't subclass ``_RobotSpecificTCodeBase`` because the robot_id parameter is used
        to resolve the tool, NOT to subsequently target the command.

    :param type: see :class: ``_TCodeBase``
    :param id: Identifier to assign to the resolved tool. This id is used in subsequent commands
        to reference this tool.
    :param descriptor: Minimal descriptor of the desired tool; resolved on the fleet.
    :param robot_id: Identifier of the robot on which to search for the tool.

    :raises ValidatorError: ``ValidatorErrorCode.ID_EXISTS`` if ``id`` is already registered to
        a tool.
    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if ``robot_id`` is not registered
        to a robot.
    """

    type: Literal["ADD_TOOL"] = "ADD_TOOL"
    id: str
    descriptor: ToolDescriptor
    robot_id: str


class ASPIRATE(_RobotSpecificTCodeBase):
    """Aspirate a given fluid volume at a given speed into the target robot's pipette.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param volume: Aspiration volume; expects volume units
    :param speed: Aspiration speed; expects volume/time units

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if ``robot_id`` is not registered
        to a robot, or if the targeted robot's currently held tool id is not registered.
    :raises ValidatorError: ``ValidatorErrorCode.TOOL_NOT_MOUNTED`` if the targeted robot is not
        currently holding a tool.
    :raises ValidatorError: ``ValidatorErrorCode.UNEXPECTED_TOOL`` if the targeted robot has a tool
        mounted that is not a pipette.
    :raises ValidatorError: ``ValidatorErrorCode.PIPETTE_TIP_NOT_MOUNTED`` if the targeted robot's
        currently held pipette does not have a pipette tip mounted.
    :raises ValidatorError: ``ValidatorErrorCode.EMPTY_PIPETTE_TIP_GROUP`` if the targeted robot's
        currently held pipette has a pipette tip group mounted with no pipette tips.
    :raises ValidatorError: ``ValidatorErrorCode.UNITS_ERROR`` if ``volume`` is not in volume units,
        or if ``speed`` is not in volume/time units.
    :raises ValidatorError: ``ValidatorErrorCode.PIPETTE_VOLUME_LIMIT_EXCEEDED`` if the targeted
        robot's currently held pipette's maximum volume is exceeded by this aspiration.
    """

    type: Literal["ASPIRATE"] = "ASPIRATE"
    volume: ValueWithUnits
    speed: ValueWithUnits


class CALIBRATE_LABWARE_HEIGHT(_RobotSpecificTCodeBase):
    """Use the target robot's currently held tool to tune the height of a target labware by probing.

    :warning: This command is not robustly tested!

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param location: The location attribute specifes which labware and where on the labware to probe.
        Unlike other location-based commands (ex. :class: MOVE_TO_LOCATION),
        :class: ``CALIBRATE_LABWARE_HEIGHT`` only supports locations that hold references to a labware.

    :param persistent: When raised, all labware of the same type and brand will be modified. If not
        raised, only the current in-place transform is applied. Restarting the tcode server will
        reset the calibration.

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if any of the following are true:
        * ``robot_id`` is not registered to a robot
        * The targeted robot's currently held tool id is not registered
        * The labware id referenced in ``location`` is not registered

    :raises ValidatorError: ``ValidatorErrorCode.TOOL_NOT_MOUNTED`` if the targeted robot is not
        currently holding a tool.

    :raises ValidatorError: ``ValidatorErrorCode.UNEXPECTED_TOOL`` if the targeted robot has a tool
        mounted that is not compatible with probing.

    :raises ValidatorError: ``ValidatorErrorCode.PIPETTE_TIP_NOT_MOUNTED`` if the targeted robot's
        currently held tool is a pipette that does not have a pipette tip mounted.

    :raises ValidatorError: ``ValidatorErrorCode.EMPTY_PIPETTE_TIP_GROUP`` if the targeted robot's
        currently held tool is a pipette that has a pipette tip group mounted with no pipette tips.
    """

    type: Literal["CALIBRATE_LABWARE_HEIGHT"] = "CALIBRATE_LABWARE_HEIGHT"
    location: LocationAsLabwareIndex | LocationRelativeToLabware
    persistent: bool


class CALIBRATE_LABWARE_WELL_DEPTH(_RobotSpecificTCodeBase):
    """Use the target robot's held tool to tune the depth of a target labware's well by probing.

    :warning: This command is not robustly tested!

    An example TCode snippet to calibrate using a pipette tip is here:
    ```
    RETRIEVE_TOOL(id=...)
    RETRIEVE_PIPETTE_TIP_GROUP(id=...)
    CALIBRATE_PIPETTE_TIP_LENGTH()
    CALIBRATE_LABWARE_WELL_DEPTH(location=LocationAsLabwareIndex(labware_id=..., location_index=...))
    ```

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param location: The location attribute specifes which labware and where on the labware to
        probe. Unlike other location-based commands (ex. :class: MOVE_TO_LOCATION),
        :class: ``CALIBRATE_LABWARE_HEIGHT`` only supports locations that hold references to a
        labware.

    :param persistent: When raised, all labware of the same type and brand will be modified. If not
        raised, only the current in-place transform is applied. Restarting the tcode server will
        reset the calibration.

    :param modify_all_wells: This flag indicates whether only the probed well's depth should be
        modified, or if the depths of all of the wells in the labware should be modified. Defaults
        to modifying all of the wells.

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if any of the following are true:
        * ``robot_id`` is not registered to a robot
        * The targeted robot's currently held tool id is not registered
        * The labware id referenced in ``location`` is not registered

    :raises ValidatorError: ``ValidatorErrorCode.TOOL_NOT_MOUNTED`` if the targeted robot is not
        currently holding a tool.

    :raises ValidatorError: ``ValidatorErrorCode.UNEXPECTED_TOOL`` if the targeted robot has a tool
        mounted that is not compatible with probing.

    :raises ValidatorError: ``ValidatorErrorCode.PIPETTE_TIP_NOT_MOUNTED`` if the targeted robot's
        currently held tool is a pipette that does not have a pipette tip mounted.

    :raises ValidatorError: ``ValidatorErrorCode.EMPTY_PIPETTE_TIP_GROUP`` if the targeted robot's
        currently held tool is a pipette that has a pipette tip group mounted with no pipette tips.
    """

    type: Literal["CALIBRATE_LABWARE_WELL_DEPTH"] = "CALIBRATE_LABWARE_WELL_DEPTH"
    location: LocationAsLabwareIndex | LocationRelativeToLabware
    persistent: bool
    modify_all_wells: bool = True


class CALIBRATE_TOOL_FOR_PROBING(_RobotSpecificTCodeBase):
    """Calibrate the target robot's currently held tool for probing.

    :note: If a bare tool is held, the tool's transform will be calibrated.
    :note: If a pipette tip is held, the pipette tip's relationship to the tool will be calibrated.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param z_only: When raised, tool is only calibrated for z-axis probing. If not raised, tool is
        calibrated for x, y, and z.

    :param persistent: When raised, the behavior is dependent on the tool mounted.
        * If a bare tool is mounted, the transform is saved to the tool's configuration.
        * If a pipette tip is mounted, the transform is applied to all pipette tips of that brand.
        * If not raised, only the currently in-place transform is applied. Restarting the tcode
            server will reset the calibration.

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if any of the following are true:
        * ``robot_id`` is not registered to a robot
        * The targeted robot's currently held tool id is not registered

    :raises ValidatorError: ``ValidatorErrorCode.TOOL_NOT_MOUNTED`` if the targeted robot is not
        currently holding a tool.

    :raises ValidatorError: ``ValidatorErrorCode.UNEXPECTED_TOOL`` if the targeted robot has a tool
        mounted that is not compatible with probing.

    :raises ValidatorError: ``ValidatorErrorCode.NOT_IMPLEMENTED`` if any of the following are true:
        * ``z_only`` is False, and the targeted robot's currently held tool is an eight-channel
            pipette
        * ``z_only`` is False, and the targeted robot's currently held tool is a pipette with a
            pipette tip group mounted
    """

    type: Literal["CALIBRATE_TOOL_FOR_PROBING"] = "CALIBRATE_TOOL_FOR_PROBING"
    z_only: bool
    persistent: bool = False


class CREATE_LABWARE(_RobotSpecificTCodeBase):
    """Create a new physical labware on the targeted robot's deck.

    :note: This command adds a labware to TCode's internal state; the description provided is NOT
        a descriptor, and is NOT resolved.

    :note: The labware will be created in the specified deck slot, and TCode will from here on
        assume that the slot is occupied by this labware.

    :warning: This command does NOT raise a ValidatorError if the target deck slot doesn't exist on
        the target robot, or if the target deck slot is already occupied. These features are coming
        in a future release.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param description: Full description of the labware to create.
        See also :class: ``LabwareDescription``.

    :param holder: The holder in which to place the new labware.

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if ``robot_id`` is not registered
        to a robot.

    :raise ValidatorError: ``ValidatorErrorCode.UNITS_ERROR`` if ``description`` contains invalid
        units data.
    """

    type: Literal["CREATE_LABWARE"] = "CREATE_LABWARE"
    description: LabwareDescription
    holder: LabwareHolder


class COMMENT(_TCodeBase):
    """A comment, included for human readability and comprehension of the TCode script.

    :param type: see :class: ``_TCodeBase``
    :param text: The comment text.
    """

    type: Literal["COMMENT"] = "COMMENT"
    text: str


class DELETE_LABWARE(_RobotSpecificTCodeBase):
    """Physically remove the labware associated with the given id from the targeted robot's deck.

    :note: This labware will no longer be available to future ADD_LABWARE resolution
    :note: TCode will assume that the holder previously occupied by this labware is now empty.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param labware_id: Identifier of the labware to remove, as previously assigned by
        ``ADD_LABWARE``.

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if ``robot_id`` is not registered to
        a robot.
    """

    type: Literal["DELETE_LABWARE"] = "DELETE_LABWARE"
    labware_id: str


class DISCARD_PIPETTE_TIP_GROUP(_RobotSpecificTCodeBase):
    """Dispose of the target robot's currently held pipette tip(s) into any accessible dry waste
        disposal location.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if any of the following are true:
        * ``robot_id`` is not registered to a robot
        * The targeted robot's currently held tool id is not registered
        * The targeted robot's currently held pipette tip group id is not registered

    :raises ValidatorError: ``ValidatorErrorCode.TOOL_NOT_MOUNTED`` if the targeted robot is not
        currently holding a tool.

    :raises ValidatorError: ``ValidatorErrorCode.UNEXPECTED_TOOL`` if the targeted robot has a tool
        mounted that is not a pipette.

    :raises ValidatorError: ``ValidatorErrorCode.PIPETTE_TIP_NOT_MOUNTED`` if the targeted robot's
        currently held pipette does not have a pipette tip mounted.

    :raises ValidatorError: ``ValidatorErrorCode.EMPTY_PIPETTE_TIP_GROUP`` if the targeted robot's
        currently held pipette has a pipette tip group mounted with no pipette tips.
    """

    type: Literal["DISCARD_PIPETTE_TIP_GROUP"] = "DISCARD_PIPETTE_TIP_GROUP"


class DISPENSE(_RobotSpecificTCodeBase):
    """Dispense a given fluid volume at a given speed from the target robot's pipette.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param volume: Dispense volume; expects volume units
    :param speed: Dispense speed; expects volume/time units

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if ``robot_id`` is not registered
        to a robot, or if the targeted robot's currently held tool id is not registered.
    :raises ValidatorError: ``ValidatorErrorCode.TOOL_NOT_MOUNTED`` if the targeted robot is not
        currently holding a tool.
    :raises ValidatorError: ``ValidatorErrorCode.UNEXPECTED_TOOL`` if the targeted robot has a tool
        mounted that is not a pipette.
    :raises ValidatorError: ``ValidatorErrorCode.PIPETTE_TIP_NOT_MOUNTED`` if the targeted robot's
        currently held pipette does not have a pipette tip mounted.
    :raises ValidatorError: ``ValidatorErrorCode.EMPTY_PIPETTE_TIP_GROUP`` if the targeted robot's
        currently held pipette has a pipette tip group mounted with no pipette tips.
    :raises ValidatorError: ``ValidatorErrorCode.UNITS_ERROR`` if ``volume`` is not in volume units,
        or if ``speed`` is not in volume/time units.
    :raises ValidatorError: ``ValidatorErrorCode.PIPETTE_VOLUME_LIMIT_EXCEEDED`` if the targeted
        robot's currently held pipette's minimum volume is exceeded by this dispense.
    """

    type: Literal["DISPENSE"] = "DISPENSE"
    volume: ValueWithUnits
    speed: ValueWithUnits


def _identity_transform() -> Matrix:
    """Generate an identity transform matrix."""
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


class MOVE_TO_LOCATION(_RobotSpecificTCodeBase):
    """Move the target robot's control point to the specified location.

    :warning: Currently, only ``location`` as a ``LocationAsLabwareIndex`` is fully validated.
        Other location types are not yet validated before runtime, and may result in unexpected
        behavior.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param location: Target location to move to.
    :param location_offset: Optional offset transform to apply to the target location before
        moving. Defaults to the identity transform.

    :param flange: Optional location describing a robot control point other than the default. If
        not specified, the robot's default control point will be used.

    :param flange_offset: Optional offset transform to apply to the flange location before
        moving. Defaults to the identity transform.

    :param path_type: Optional path type to use during the move. See ``PathType`` enum for options.
        defaults to the ``PathType.SAFE`` if not given.

    :param trajectory_type: Optional trajectory type to use during the move. See ``TrajectoryType``
        enum for options. Defaults to the robot's default trajectory type if not given.

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if any of the following are true:
        * ``robot_id`` is not registered to a robot
        * ``location`` is a ``LocationAsLabwareIndex`` and the referenced labware id is not yet
            registered.
        * ``location`` is a ``LocationAsLabwareIndex`` and the ``location_index`` is out of bounds

    :raises ValidatorError: ``ValidatorErrorCode.TRANSFORM_SIZE_LIMIT_EXCEEDED`` if either
        ``location_offset`` or ``flange_offset`` contains a linear distance exceeding 100 mm.

    :raises ValidatorError: ``ValidatorErrorCode.UNEXPECTED_LABWARE_TYPE`` if ``location`` is a
        ``LocationAsLabwareIndex`` and the referenced labware is not a type that supports indexing.
        (ex. AGAR_PLATE)
    """

    type: Literal["MOVE_TO_LOCATION"] = "MOVE_TO_LOCATION"
    location: Location
    location_offset: Matrix = Field(default_factory=_identity_transform)
    flange: Location | None = None
    flange_offset: Matrix = Field(default_factory=_identity_transform)
    path_type: int | None = None  # PathType | None = None
    trajectory_type: int | None = None  # TrajectoryType | None = None


class MOVE_TO_JOINT_POSE(_RobotSpecificTCodeBase):
    """Move the target robot to the specified joint positions.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param joint_positions: List of joint positions to move to; expects joint-specific position
        units for SCARA-type robots.

    :param relative: When true, the joint positions are interpreted as relative offsets from the
        robot's current joint positions. When false, the joint positions are interpreted as absolute
        positions.

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if ``robot_id`` is not registered
        to a robot.

    :raises ValidatorError: ``ValidatorErrorCode.JOINT_COUNT_MISMATCH`` if the length of
        ``joint_positions`` is not four.

    :raises ValidatorError: ``ValidatorErrorCode.UNITS_ERROR`` if any of the values in
        ``joint_positions`` are not in joint-specific position units (length | angle).
    """

    type: Literal["MOVE_TO_JOINT_POSE"] = "MOVE_TO_JOINT_POSE"
    joint_positions: list[ValueWithUnits]
    relative: bool


class PAUSE(_TCodeBase):
    """Pause execution until resumed by the user.

    While ``WAIT`` delays a target robot for a set duration, ``PAUSE`` halts the entire fleet
    until the user manually resumes execution.

    :param type: see :class: ``_TCodeBase``
    """

    type: Literal["PAUSE"] = "PAUSE"


class PICK_UP_LABWARE(_RobotSpecificTCodeBase):
    """Pick up the target labware with the target robot's currently held plate gripper.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param labware_id: Identifier of the labware to pick up, as previously assigned by
        ``ADD_LABWARE``.
    :param grasp_type: Optional grasp type to use when picking up the labware. See
        :class: ``GraspType`` enum for options. Defaults to ``GraspType.UNSPECIFIED``.

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if any of the following are true:
        * ``robot_id`` is not registered to a robot
        * The targeted robot's currently held tool id is not registered
        * ``labware_id`` is not registered to a labware

    :raises ValidatorError: ``ValidatorErrorCode.TOOL_NOT_MOUNTED`` if the targeted robot is not
        currently holding a tool.
    :raises ValidatorError: ``ValidatorErrorCode.UNEXPECTED_TOOL`` if the targeted robot has a tool
        mounted that is not a plate gripper.
    """

    type: Literal["PICK_UP_LABWARE"] = "PICK_UP_LABWARE"
    labware_id: str
    grasp_type: str = GraspType.UNSPECIFIED.value


class PUT_DOWN_LABWARE(_RobotSpecificTCodeBase):
    """Put down the target robot's currently held labware at the specified location.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param holder: Holder in which to put down the labware.
        :warning: The holder is currently unverified!

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if any of the following are true:
        * ``robot_id`` is not registered to a robot
        * The targeted robot's currently held tool id is not registered

    :raises ValidatorError: ``ValidatorErrorCode.TOOL_NOT_MOUNTED`` if the targeted robot is not
        currently holding a tool.

    :raises ValidatorError: ``ValidatorErrorCode.UNEXPECTED_TOOL`` if the targeted robot has a tool
        mounted that is not a plate gripper.

    :raises ValidatorError: ``ValidatorErrorCode.UNNECESSARY`` it the targeted robot is  has a
        plate gripper that is not holding a labware.
    """

    type: Literal["PUT_DOWN_LABWARE"] = "PUT_DOWN_LABWARE"
    holder: LabwareHolder


class REMOVE_LABWARE_LID(_RobotSpecificTCodeBase):
    """Remove the lid from the target labware.

    :error: This command is not yet implemented, and will always raise a ``ValidatorError`` with
        code ``ValidatorErrorCode.NOT_IMPLEMENTED``.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param labware_id: Identifier of the labware from which to remove the lid, as previously
        assigned by ``ADD_LABWARE``.
    :param storage_holder: Optional holder at which to store the removed lid. If not specified,
        the lid will be stored in a default holder, if available.

    raises ValidatorError: ``ValidatorErrorCode.NOT_IMPLEMENTED`` all the time.
    """

    type: Literal["REMOVE_LABWARE_LID"] = "REMOVE_LABWARE_LID"
    labware_id: str
    storage_holder: LabwareHolder | None = None


class REPLACE_LABWARE_LID(_RobotSpecificTCodeBase):
    """Replace the lid on the target labware.

    :error: This command is not yet implemented, and will always raise a ``ValidatorError`` with
        code ``ValidatorErrorCode.NOT_IMPLEMENTED``.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param labware_id: Identifier of the labware on which to replace the lid, as previously
        assigned by ``ADD_LABWARE``.
    :param lid_id: Optional identifier of the lid to replace. If not specified, the most recently
        removed lid will be used, if available.`

    raises ValidatorError: ``ValidatorErrorCode.NOT_IMPLEMENTED`` all the time.
    """

    type: Literal["REPLACE_LABWARE_LID"] = "REPLACE_LABWARE_LID"
    labware_id: str
    lid_id: str | None = None


class PICK_UP_PIPETTE_TIP(_RobotSpecificTCodeBase):
    """Pick up pipette tip(s) with the target robot's currently held pipette at the specified
        location.

    :note: This is a lower-level TCode command - most users are suggested to use
        :class: ``RETRIEVE_PIPETTE_TIP_GROUP`` instead.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param location: Location at which to pick up the pipette tip(s).
        :warning: The location is currently unverified!

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if any of the following are true:
        * ``robot_id`` is not registered to a robot
        * The targeted robot's currently held tool id is not registered

    :raises ValidatorError: ``ValidatorErrorCode.TOOL_NOT_MOUNTED`` if the targeted robot is not
        currently holding a tool.

    :raises ValidatorError: ``ValidatorErrorCode.UNEXPECTED_TOOL`` if the targeted robot has a tool
        mounted that is not a pipette.

    :raises ValidatorError: ``ValidatorErrorCode.UNEXPECTED_PIPETTE_TIP`` if the targeted robot
        is currently holding a pipette tip group.
    """

    type: Literal["PICK_UP_PIPETTE_TIP"] = "PICK_UP_PIPETTE_TIP"
    location: Location


class PUT_DOWN_PIPETTE_TIP(_RobotSpecificTCodeBase):
    """Put down the target robot's currently held pipette tip(s) at the specified location.

    :note: This is a lower-level TCode command - most users are suggested to use
        :class: ``RETURN_PIPETTE_TIP_GROUP`` or :class: ``DISCARD_PIPETTE_TIP_GROUP`` instead.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param location: Location at which to put down the pipette tip(s).
        :warning: The location is currently unverified!

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if any of the following are true:
        * ``robot_id`` is not registered to a robot
        * The targeted robot's currently held tool id is not registered
        * The targeted robot's currently held pipette tip group id is not registered

    :raises ValidatorError: ``ValidatorErrorCode.TOOL_NOT_MOUNTED`` if the targeted robot is not
        currently holding a tool.

    :raises ValidatorError: ``ValidatorErrorCode.UNEXPECTED_TOOL`` if the targeted robot has a tool
        mounted that is not a pipette.

    :raises ValidatorError: ``ValidatorErrorCode.PIPETTE_TIP_NOT_MOUNTED`` if the targeted robot's
        currently held pipette does not have a pipette tip mounted.

    :raises ValidatorError: ``ValidatorErrorCode.EMPTY_PIPETTE_TIP_GROUP`` if the targeted robot's
        currently held pipette has a pipette tip group mounted with no pipette tips.
    """

    type: Literal["PUT_DOWN_PIPETTE_TIP"] = "PUT_DOWN_PIPETTE_TIP"
    location: Location


class RETRIEVE_PIPETTE_TIP_GROUP(_RobotSpecificTCodeBase):
    """Pick up the target pipette tip group using the target robot's currently held pipette.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param id: Target pipette tip group identifier.

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if any of the following are true:
        * ``robot_id`` is not registered to a robot
        * The targeted robot's currently held tool id is not registered
        * ``id`` is not registered to a pipette tip group

    :raises ValidatorError: ``ValidatorErrorCode.TOOL_NOT_MOUNTED`` if the targeted robot is not
        currently holding a tool.

    :raises ValidatorError: ``ValidatorErrorCode.UNEXPECTED_TOOL`` if the targeted robot has a tool
        mounted that is not a pipette.

    :raises ValidatorError: ``ValidatorErrorCode.UNEXPECTED_PIPETTE_TIP_GROUP`` if the targeted
        robot is currently holding a pipette tip group.
    """

    type: Literal["RETRIEVE_PIPETTE_TIP_GROUP"] = "RETRIEVE_PIPETTE_TIP_GROUP"
    id: str


class RETRIEVE_TOOL(_RobotSpecificTCodeBase):
    """Pick up the target tool using the target robot's empty flange.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param id: Target tool identifier.

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if any of the following are true:
        * ``robot_id`` is not registered to a robot
        * ``id`` is not registered to a tool

    :raises ValidatorError: ``ValidatorErrorCode.UNNECESSARY`` if the targeted robot is already
        holding the targeted tool.

    :raises ValidatorError: ``ValidatorErrorCode.WRONG_TOOL_MOUNTED`` if the targeted robot is
        currently holding a tool that is not the targeted tool.
    """

    type: Literal["RETRIEVE_TOOL"] = "RETRIEVE_TOOL"
    id: str


class RETURN_PIPETTE_TIP_GROUP(_RobotSpecificTCodeBase):
    """Return the pipette tip group currently held by the target robot to the location from which
        it was picked up.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if any of the following are true:
        * ``robot_id`` is not registered to a robot
        * The targeted robot's currently held tool id is not registered
        * The targeted robot's currently held pipette tip group id is not registered

    :raises ValidatorError: ``ValidatorErrorCode.TOOL_NOT_MOUNTED`` if the targeted robot is not
        currently holding a tool.

    :raises ValidatorError: ``ValidatorErrorCode.UNEXPECTED_TOOL`` if the targeted robot has a tool
        mounted that is not a pipette.

    :raises ValidatorError: ``ValidatorErrorCode.PIPETTE_TIP_NOT_MOUNTED`` if the targeted robot's
        currently held pipette does not have a pipette tip mounted.

    :raises ValidatorError: ``ValidatorErrorCode.EMPTY_PIPETTE_TIP_GROUP`` if the targeted robot's
        currently held pipette has a pipette tip group mounted with no pipette tips.
    """

    type: Literal["RETURN_PIPETTE_TIP_GROUP"] = "RETURN_PIPETTE_TIP_GROUP"


class RETURN_TOOL(_RobotSpecificTCodeBase):
    """Return the tool currently held by the target robot to the tool rack.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if any of the following are true:
        * ``robot_id`` is not registered to a robot
        * The targeted robot's currently held tool id is not registered

    :raises ValidatorError: ``ValidatorErrorCode.UNNECESSARY`` if the targeted robot is already
        holding the targeted tool.

    :raises ValidatorError: ``ValidatorErrorCode.UNEXPECTED_PIPETTE_TIP_GROUP`` if the targeted
        robot is currently holding a pipette with a pipette tip group.

    :raises ValidatorError: ``ValidatorErrorCode.UNEXPECTED_LABWARE`` if the targeted robot is
        currently holding a plate gripper which is in turn holding a labware.
    """

    type: Literal["RETURN_TOOL"] = "RETURN_TOOL"


class SWAP_TO_TOOL(_RobotSpecificTCodeBase):
    """Return any tool currently held by the target robot to the tool rack, then pick up the target
        tool using the target robot's empty flange.

    :warning: This command doesn't yet have all of the validation functionality of ``RETRIEVE_TOOL``
        and ``RETURN_TOOL`` - for example, it doesn't yet error if the robot is holding a pipette
        with a pipette tip group, or a plate gripper holding a labware.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param id: Target tool identifier.

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if any of the following are true:
        * ``robot_id`` is not registered to a robot
        * ``id`` is not registered to a tool

    :raises ValidatorError: ``ValidatorErrorCode.UNNECESSARY`` if the targeted robot is already
        holding the targeted tool.
    """

    type: Literal["SWAP_TO_TOOL"] = "SWAP_TO_TOOL"
    id: str


class WAIT(_RobotSpecificTCodeBase):
    """Delay the subsequent commands to the target robot for the specified duration.

    :param type: see :class: ``_TCodeBase``
    :param robot_id: see :class: ``_RobotSpecificTCodeBase``
    :param duration: Duration to wait; expects time units

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if ``robot_id`` is not registered
        to a robot.
    :raises ValidatorError: ``ValidatorErrorCode.UNITS_ERROR`` if ``duration`` is not in time units.
    """

    type: Literal["WAIT"] = "WAIT"
    duration: ValueWithUnits


class WebHookBody(BaseModel):
    """The webhook request that is sent out with SEND_WEBHOOK

    :param timestamp: UNIX timestamp of the request in seconds
    :param fleet_name: Name of the fleet controller that triggered the request
    :param destination_url: The destination URL of this request as specified in TCode
    :param is_execution_paused: Whether the execution of the script is paused
    :param payload: The custom message as specified
    """

    timestamp: float
    fleet_name: str
    destination_url: str
    is_execution_paused: bool
    payload: str | None


class SEND_WEBHOOK(_TCodeBase):
    """Send a webhook call to the specified URL with the specified payload

    :param type: see :class: ``_TCodeBase``
    :param pause_execution: whether to pause execution of the script when this command is run
    :param url: The URL to send the request to
    :param payload: An optional payload to include in the request. The maximum payload size is 32KiB

    On encountering command, the scheduler will send an HTTP POST request to
    the specified URL with a JSON body as specified in :class:`WebHookBody`

    """

    type: Literal["SEND_WEBHOOK"] = "SEND_WEBHOOK"
    pause_execution: bool
    url: str
    payload: str | None = None


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
    | SEND_WEBHOOK
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

    @classmethod
    def new(cls, name: str, description: str | None = None) -> TCodeScript:
        """Create a new, empty TCode script with the given name and optional description.

        :param name: Name of the TCode script.
        :param description: Optional description of the TCode script.

        :returns: A new, empty TCode script.
        """
        metadata = Metadata(
            name=name,
            description=description,
            timestamp=datetime.datetime.now().isoformat(),
            tcode_api_version=importlib.metadata.version("tcode_api"),
        )

        return cls(metadata=metadata, commands=[])

    @classmethod
    def read(cls, file_object: TextIO) -> TCodeScript:
        """Load a TCode script from a file-like object.

        :param file_object: A file-like object containing the TCode script.

        :returns: The loaded TCode script.
        """
        data = file_object.read()
        script = cls.model_validate_json(data)
        current_version = importlib.metadata.version("tcode_api")
        if script.metadata.tcode_api_version != current_version:
            _logger.warning(
                "Loaded TCode script was created with API version %s, current version is %s",
                script.metadata.tcode_api_version,
                current_version,
            )
        return script

    def write(self, file_object: TextIO) -> None:
        """Write the TCode script to a file-like object.

        :param file_object: A file-like object to which to write the TCode script.
        """
        data = self.model_dump_json(indent=2)
        file_object.write(data)
