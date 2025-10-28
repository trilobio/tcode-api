"""Generate Basic Fluid Movement TCode script for unittesting."""

import tcode_api.api as tc
from tcode_api.servicer import TCodeServicerClient
from tcode_api.utilities import (
    create_transform,
    describe_pipette_tip_box,
    describe_well_plate,
    generate_id,
    labware_loader,
    location_as_labware_index,
    mm,
    ul,
    ul_per_s,
)

pipette_volume = ul(300)
blowout_volume = ul(20)
transfer_volume = ul(100)
channel_count = 1
pipette_descriptor = tc.SingleChannelPipetteDescriptor(max_volume=pipette_volume)
well_bottom_offset = create_transform(z=mm(3))

script = tc.TCodeScript.new(
    name=f"Fluid Transfer (C1P{pipette_volume.magnitude})",
)
(
    robot_id,
    pipette_id,
    plate_id,
    tip_box_id,
    pipette_tip_group_id_1,
    trash_can_id,
    trough_id,
) = [generate_id() for _ in range(7)]

# Resolve robot and pipette
script.commands.append(tc.ADD_ROBOT(id=robot_id, descriptor=tc.RobotDescriptor()))
script.commands.append(
    tc.ADD_TOOL(
        robot_id=robot_id,
        id=pipette_id,
        descriptor=pipette_descriptor,
    )
)

# Create labware
script.commands.append(
    tc.CREATE_LABWARE(
        robot_id=robot_id,
        description=labware_loader.load("costar_3603_plate"),
        holder=tc.LabwareHolderName(robot_id=robot_id, name="DeckSlot_5"),
    )
)
script.commands.append(
    tc.CREATE_LABWARE(
        robot_id=robot_id,
        description=labware_loader.load("biotix_utip_p300_box"),
        holder=tc.LabwareHolderName(robot_id=robot_id, name="DeckSlot_8"),
    )
)
script.commands.append(
    tc.CREATE_LABWARE(
        robot_id=robot_id,
        description=labware_loader.load("mtcbiotech_4_channel_trough"),
        holder=tc.LabwareHolderName(robot_id=robot_id, name="DeckSlot_6"),
    )
)
script.commands.append(
    tc.CREATE_LABWARE(
        robot_id=robot_id,
        description=labware_loader.load("3d_printed_trash_can"),
        holder=tc.LabwareHolderName(robot_id=robot_id, name="DeckSlot_11"),
    )
)

# Resolve labware
script.commands.append(tc.ADD_LABWARE(id=plate_id, descriptor=describe_well_plate()))
script.commands.append(
    tc.ADD_LABWARE(id=tip_box_id, descriptor=describe_pipette_tip_box(full=True))
)
script.commands.append(tc.ADD_LABWARE(id=trash_can_id, descriptor=tc.TrashDescriptor()))
script.commands.append(
    tc.ADD_LABWARE(
        id=trough_id,
        descriptor=tc.WellPlateDescriptor(
            named_tags={"name": ""},
        ),
    )
)
script.commands.append(
    tc.ADD_PIPETTE_TIP_GROUP(
        id=pipette_tip_group_id_1,
        descriptor=tc.PipetteTipGroupDescriptor(
            row_count=channel_count,
            column_count=1,
        ),
    )
)
#  Actions
script.commands.append(tc.RETRIEVE_TOOL(robot_id=robot_id, id=pipette_id))
script.commands.append(
    tc.RETRIEVE_PIPETTE_TIP_GROUP(id=pipette_tip_group_id_1, robot_id=robot_id)
)
script.commands.append(
    tc.MOVE_TO_LOCATION(
        robot_id=robot_id,
        location=location_as_labware_index(trough_id, 0, tc.WellPartType.TOP),
    )
)
script.commands.append(
    tc.ASPIRATE(robot_id=robot_id, volume=blowout_volume, speed=ul_per_s(25))
)
script.commands.append(
    tc.MOVE_TO_LOCATION(
        robot_id=robot_id,
        location=location_as_labware_index(trough_id, 0, tc.WellPartType.BOTTOM),
        path_type=tc.PathType.DIRECT,
        location_offset=well_bottom_offset,
    )
)
script.commands.append(
    tc.ASPIRATE(robot_id=robot_id, volume=transfer_volume, speed=ul_per_s(25))
)
script.commands.append(
    tc.MOVE_TO_LOCATION(
        robot_id=robot_id,
        location=location_as_labware_index(plate_id, 1, tc.WellPartType.BOTTOM),
        location_offset=well_bottom_offset,
    )
)
script.commands.append(
    tc.DISPENSE(robot_id=robot_id, volume=transfer_volume, speed=ul_per_s(25))
)
script.commands.append(
    tc.MOVE_TO_LOCATION(
        robot_id=robot_id,
        location=location_as_labware_index(plate_id, 1, tc.WellPartType.TOP),
        path_type=tc.PathType.DIRECT,
    )
)
script.commands.append(
    tc.DISPENSE(robot_id=robot_id, volume=blowout_volume, speed=ul_per_s(25))
)
script.commands.append(tc.DISCARD_PIPETTE_TIP_GROUP(robot_id=robot_id))
script.commands.append(tc.RETURN_TOOL(robot_id=robot_id))

# Run the script
client = TCodeServicerClient("http://192.168.8.157:8002")

# Set up stuff
client.clear_schedule()
client.clear_labware()
client.clear_tcode_resolution()
client.discover_fleet()

for command in script.commands:
    rsp = client.schedule_command(generate_id(), command)
    if not rsp.result.success:
        raise RuntimeError(rsp)
client.execute_run_loop()
