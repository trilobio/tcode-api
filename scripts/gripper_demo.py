"""TCode demonstration script of moving labware on deck."""

import tcode_api.api as tc
from tcode_api.script import TCodeScriptBuilder
from tcode_api.servicer import TCodeServicerClient
from tcode_api.utilities import describe_well_plate, generate_id, labware_loader

builder = TCodeScriptBuilder(name="Gripper Demo")

# FLEET
robot_id, gripper_id, labware_id = [generate_id() for _ in range(3)]
builder.add_command(tc.ADD_ROBOT(id=robot_id, descriptor=tc.RobotDescriptor()))
builder.add_command(
    tc.ADD_TOOL(robot_id=robot_id, id=gripper_id, descriptor=tc.GripperDescriptor())
)

# LABWARE
builder.add_command(
    tc.CREATE_LABWARE(
        robot_id=robot_id,
        description=labware_loader.load("costar_3603_plate"),
        holder=tc.LabwareHolderName(
            robot_id=robot_id,
            name="DeckSlot_1",
        ),
    ),
)
builder.add_command(
    tc.ADD_LABWARE(id=labware_id, descriptor=describe_well_plate(has_lid=True))
)

# ACTIONS #
builder.add_command(tc.SWAP_TO_TOOL(robot_id=robot_id, id=gripper_id))
builder.add_command(tc.COMMENT(text="Move labware with lift"))
builder.add_command(tc.PICK_UP_LABWARE(robot_id=robot_id, labware_id=labware_id))
builder.add_command(
    tc.PUT_DOWN_LABWARE(
        robot_id=robot_id,
        holder=tc.LabwareHolderName(
            robot_id=robot_id,
            name="DeckSlot_2",
        ),
    )
)
builder.add_command(tc.COMMENT(text="Move labware with pinch"))
builder.add_command(
    tc.PICK_UP_LABWARE(
        robot_id=robot_id, labware_id=labware_id, grasp_type=tc.GraspType.PINCH
    )
)
builder.add_command(
    tc.PUT_DOWN_LABWARE(
        robot_id=robot_id,
        holder=tc.LabwareHolderName(
            robot_id=robot_id,
            name="DeckSlot_1",
        ),
    )
)
builder.add_command(tc.RETURN_TOOL(robot_id=robot_id))

# Run the script
client = TCodeServicerClient("http://192.168.8.157:8002")

# Set up stuff
client.clear_schedule()
client.clear_labware()
client.clear_tcode_resolution()
client.discover_fleet()

for command in builder.emit().commands:
    rsp = client.schedule_command(generate_id(), command)
    if not rsp.result.success:
        raise RuntimeError(rsp)

client.execute_run_loop()
