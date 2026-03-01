from typing import Annotated

from pydantic import Field

from .add_labware.latest import ADD_LABWARE
from .add_pipette_tip_group.latest import ADD_PIPETTE_TIP_GROUP
from .add_robot.latest import ADD_ROBOT
from .add_tool.latest import ADD_TOOL
from .aspirate.latest import ASPIRATE
from .calibrate_labware_height.latest import (
    CALIBRATE_LABWARE_HEIGHT,
)
from .calibrate_labware_well_depth.latest import (
    CALIBRATE_LABWARE_WELL_DEPTH,
)
from .calibrate_tool_for_probing.latest import (
    CALIBRATE_TOOL_FOR_PROBING,
)
from .comment.latest import COMMENT
from .create_labware.latest import CREATE_LABWARE
from .delete_labware.latest import DELETE_LABWARE
from .discard_pipette_tip_group.latest import (
    DISCARD_PIPETTE_TIP_GROUP,
)
from .dispense.latest import DISPENSE
from .move_gripper.latest import MOVE_GRIPPER
from .move_to_joint_pose.latest import MOVE_TO_JOINT_POSE
from .move_to_location.latest import MOVE_TO_LOCATION
from .pause.latest import PAUSE
from .pick_up_labware.latest import PICK_UP_LABWARE
from .pick_up_pipette_tip.latest import PICK_UP_PIPETTE_TIP
from .put_down_labware.latest import PUT_DOWN_LABWARE
from .put_down_pipette_tip.latest import PUT_DOWN_PIPETTE_TIP
from .remove_labware_lid.latest import REMOVE_LABWARE_LID
from .replace_labware_lid.latest import REPLACE_LABWARE_LID
from .retrieve_pipette_tip_group.latest import (
    RETRIEVE_PIPETTE_TIP_GROUP,
)
from .retrieve_tool.latest import RETRIEVE_TOOL
from .return_pipette_tip_group.latest import (
    RETURN_PIPETTE_TIP_GROUP,
)
from .return_tool.latest import RETURN_TOOL
from .send_webhook.latest import SEND_WEBHOOK
from .swap_to_tool.latest import SWAP_TO_TOOL
from .wait.latest import WAIT

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
    | MOVE_GRIPPER
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
    Field(discriminator="type", description="Union type of all valid TCode commands."),
]
