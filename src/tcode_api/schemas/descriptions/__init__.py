"""TCode entity and labware description/descriptor schemas."""

# This module re-exports all description and descriptor classes from their versioned submodules.
# The __init__.py structure at each schemas submodule level is maintained explicitly
# to support Sphinx automodule autodoc generation for the tcode_api documentation.

from .axis_aligned_rectangle.latest import (
    AxisAlignedRectangleDescription,
    AxisAlignedRectangleDescriptor,
)
from .circle.latest import CircleDescription, CircleDescriptor
from .grid.latest import GridDescription, GridDescriptor
from .labware.lid.latest import LidDescription, LidDescriptor
from .labware.pipette_tip_box.latest import (
    PipetteTipBoxDescription,
    PipetteTipBoxDescriptor,
)
from .labware.trash.latest import TrashDescription, TrashDescriptor
from .labware.tube_holder.latest import TubeHolderDescription, TubeHolderDescriptor
from .labware.union import LabwareDescription, LabwareDescriptor
from .labware.well_plate.latest import WellPlateDescription, WellPlateDescriptor
from .labware_holder.latest import LabwareHolderDescriptor
from .pipette_tip.latest import PipetteTipDescription, PipetteTipDescriptor
from .pipette_tip_group.latest import PipetteTipGroupDescriptor
from .robot.latest import RobotDescriptor
from .tool.gripper.latest import GripperDescriptor
from .tool.pipette.eight_channel_pipette.latest import EightChannelPipetteDescriptor
from .tool.pipette.single_channel_pipette.latest import SingleChannelPipetteDescriptor
from .tool.pipette.union import PipetteDescriptor
from .tool.probe.latest import ProbeDescriptor
from .tool.union import ToolDescriptor
from .tool_holder.latest import ToolHolderDescriptor
from .tube.latest import TubeDescription, TubeDescriptor
from .union import WellShapeDescription, WellShapeDescriptor
from .well.latest import WellDescription, WellDescriptor
from .well_bottom.conical_bottom.latest import (
    ConicalBottomDescription,
    ConicalBottomDescriptor,
)
from .well_bottom.flat_bottom.latest import FlatBottomDescription, FlatBottomDescriptor
from .well_bottom.round_bottom.latest import (
    RoundBottomDescription,
    RoundBottomDescriptor,
)
from .well_bottom.union import WellBottomShapeDescription, WellBottomShapeDescriptor
from .well_bottom.v_bottom.latest import VBottomDescription, VBottomDescriptor

__all__ = [
    "AxisAlignedRectangleDescription",
    "AxisAlignedRectangleDescriptor",
    "CircleDescription",
    "CircleDescriptor",
    "ConicalBottomDescription",
    "ConicalBottomDescriptor",
    "EightChannelPipetteDescriptor",
    "FlatBottomDescription",
    "FlatBottomDescriptor",
    "GridDescription",
    "GridDescriptor",
    "GripperDescriptor",
    "LabwareDescription",
    "LabwareDescriptor",
    "LabwareHolderDescriptor",
    "LidDescription",
    "LidDescriptor",
    "PipetteDescriptor",
    "PipetteTipBoxDescription",
    "PipetteTipBoxDescriptor",
    "PipetteTipDescription",
    "PipetteTipDescriptor",
    "PipetteTipGroupDescriptor",
    "ProbeDescriptor",
    "RobotDescriptor",
    "RoundBottomDescription",
    "RoundBottomDescriptor",
    "SingleChannelPipetteDescriptor",
    "ToolDescriptor",
    "ToolHolderDescriptor",
    "TrashDescription",
    "TrashDescriptor",
    "TubeDescription",
    "TubeDescriptor",
    "TubeHolderDescription",
    "TubeHolderDescriptor",
    "VBottomDescription",
    "VBottomDescriptor",
    "WellBottomShapeDescription",
    "WellBottomShapeDescriptor",
    "WellDescription",
    "WellDescriptor",
    "WellPlateDescription",
    "WellPlateDescriptor",
    "WellShapeDescription",
    "WellShapeDescriptor",
]
