from typing import Literal

from pydantic import Field

from ...location.location_as_labware_holder.v1 import LocationAsLabwareHolder
from ..base import BaseRobotSpecificTCodeCommand


class CALIBRATE_LABWARE_HOLDER(BaseRobotSpecificTCodeCommand):
    """Calibrate the position of a target labware holder (deck slot) on the target robot by probing
    or by teaching.

    - If a probe is held by the robot, the calibration will be performed by probing.
    - If a pipette is held by the robot, the calibration will be performed by teaching.
        - Only X, Y, and rotation around Z will be calibrated.
        - A tip box must be registered in the target holder

    The pipette teach procedure is as follows:
    - Single Channel Pipette:
        - Move the pipette manifold to the center of the A1 tip location
        - Confirm via the UI that the pipette is in position
        - Move the pipette manifold to the center of the H12 tip location
        - Confirm via the UI that the pipette is in position
    - 8-Channel Pipette:
        - Move the pipette manifold to the center of the A1 tip location
        - Confirm via the UI that the pipette is in position
        - Move the pipette manifold to the center of the A12 tip location
        - Confirm via the UI that the pipette is in position

    NOTE: The UI confirmation steps are done via a websocket connection to the Tcode server

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if any of the following are true:
        * ``robot_id`` is not registered to a robot
        * The labware holder id referenced in ``location`` is not registered on the target robot

    :raises ValidatorError: ``ValidatorErrorCode.UNEXPECTED_TOOL`` if the targeted robot has a tool
        mounted that is not compatible with probing or teaching.
    """

    type: Literal["CALIBRATE_LABWARE_HOLDER"] = "CALIBRATE_LABWARE_HOLDER"
    schema_version: Literal[1] = 1
    location: LocationAsLabwareHolder = Field(
        description="The labware holder (probably a deck slot) to calibrate.",
    )
