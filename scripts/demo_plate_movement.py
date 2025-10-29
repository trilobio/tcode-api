"""Demonstrate using a labware gripper to move a plate by lifting and pinching."""

import tcode_api.api as tc
from tcode_api.servicer import TCodeServicerClient
from tcode_api.utilities import describe_well_plate, generate_id, labware_loader

script = tc.TCodeScript.new(
    name=__file__,
    description=__doc__,
)

# FLEET
robot_id, gripper_id, labware_id = [generate_id() for _ in range(3)]
script.commands.append(tc.ADD_ROBOT(id=robot_id, descriptor=tc.RobotDescriptor()))
script.commands.append(
    tc.ADD_TOOL(robot_id=robot_id, id=gripper_id, descriptor=tc.GripperDescriptor())
)

# LABWARE
script.commands.append(
    tc.CREATE_LABWARE(
        robot_id=robot_id,
        description=labware_loader.load("costar_3603_plate"),
        holder=tc.LabwareHolderName(
            robot_id=robot_id,
            name="DeckSlot_1",
        ),
    ),
)
script.commands.append(tc.ADD_LABWARE(id=labware_id, descriptor=describe_well_plate(has_lid=True)))

# ACTIONS #
script.commands.append(tc.SWAP_TO_TOOL(robot_id=robot_id, id=gripper_id))
script.commands.append(tc.COMMENT(text="Move labware with lift"))
script.commands.append(tc.PICK_UP_LABWARE(robot_id=robot_id, labware_id=labware_id))
script.commands.append(
    tc.PUT_DOWN_LABWARE(
        robot_id=robot_id,
        holder=tc.LabwareHolderName(
            robot_id=robot_id,
            name="DeckSlot_2",
        ),
    )
)
script.commands.append(tc.COMMENT(text="Move labware with pinch"))
script.commands.append(
    tc.PICK_UP_LABWARE(robot_id=robot_id, labware_id=labware_id, grasp_type=tc.GraspType.PINCH)
)
script.commands.append(
    tc.PUT_DOWN_LABWARE(
        robot_id=robot_id,
        holder=tc.LabwareHolderName(
            robot_id=robot_id,
            name="DeckSlot_1",
        ),
    )
)
script.commands.append(tc.RETURN_TOOL(robot_id=robot_id))

# Run the script
client = TCodeServicerClient()
client.run_script(script)
