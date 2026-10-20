"""Swap to specified tool.

This script causes the robot to pick up a specified tool, dropping off any tool that is currently
attached. The tool can be a gripper, a pipette, or a probe. If 'none' is specified, the robot will
not pick up another tool after drop-off.
"""

import logging
import pathlib

import plac  # type: ignore [import-untyped]

import tcode_api.api as tc
from tcode_api.cli import (
    DEFAULT_SERVICER_URL,
    output_file_path_annotation,
    robot_serial_number_annotation,
    servicer_url_annotation,
)
from tcode_api.servicer import TCodeServicerClient
from tcode_api.utilities import generate_id, ul

_logger = logging.getLogger(__name__)


TOOL_CHOICES = {
    "gripper": tc.GripperDescriptor(),
    "c1p300": tc.SingleChannelPipetteDescriptor(max_volume=ul(300)),
    "c8p300": tc.EightChannelPipetteDescriptor(max_volume=ul(300)),
    "c1p20": tc.SingleChannelPipetteDescriptor(max_volume=ul(20)),
    "c8p20": tc.EightChannelPipetteDescriptor(max_volume=ul(20)),
    "c1p1000": tc.SingleChannelPipetteDescriptor(max_volume=ul(1000)),
    "c8p1000": tc.EightChannelPipetteDescriptor(max_volume=ul(1000)),
    "probe": tc.ProbeDescriptor(),
    "none": None,
}


@plac.annotations(
    tool_name=plac.Annotation(
        "Name of tool to swap to (ex. 'gripper', 'c1p300', 'probe', 'none')",
        choices=list(TOOL_CHOICES.keys()),
    ),
    servicer_url=servicer_url_annotation,
    output_file_path=output_file_path_annotation,
    robot_sn=robot_serial_number_annotation,
)
def main(
    tool_name: str,
    servicer_url: str = DEFAULT_SERVICER_URL,
    output_file_path: pathlib.Path | None = None,
    robot_sn: str | None = None,
) -> None:
    """Generate and run a minimal script to pick up one tip."""

    script = tc.TCodeScript.new(name=f"Swap to {tool_name}", description=__doc__)
    script.commands += [
        tc.ADD_ROBOT(
            id=(robot_id := generate_id()), descriptor=tc.RobotDescriptor(serial_number=robot_sn)
        ),
    ]
    if (descriptor := TOOL_CHOICES.get(tool_name)) is not None:
        script.commands += [
            tc.ADD_TOOL(robot_id=robot_id, id=(tool_id := generate_id()), descriptor=descriptor),
            tc.SWAP_TO_TOOL(robot_id=robot_id, id=tool_id),
        ]
    else:
        raise NotImplementedError("Currently unable to swap to 'none' tool.")

    if output_file_path is not None:
        with output_file_path.open("w") as f:
            script.write(f)

    client = TCodeServicerClient(servicer_url=servicer_url)
    client.run_script(script)


if __name__ == "__main__":
    plac.call(main)
