"""Human-readable scripting wrapper for the TCode API."""

import importlib.metadata
import logging
import pathlib
import time
from difflib import get_close_matches

from tcode_api.api import (
    ASPIRATE,
    DISPENSE,
    DROP_TIP,
    DROP_TOOL,
    GET_TIP,
    GET_TOOL,
    GOTO,
    Fleet,
    Labware,
    Location,
    LocationType,
    Metadata,
    PathType,
    Robot,
    TCodeAST,
    Tool,
    TrajectoryType,
    ValueWithUnits,
)

_logger = logging.getLogger("tcode.script")


def load_tcode_json_file(file_path: pathlib.Path) -> TCodeAST:
    """Load a TCode AST from a json file."""
    file_path = file_path.resolve()
    if not file_path.is_file():
        matches = get_close_matches(
            file_path.name, [f.name for f in file_path.parent.iterdir()]
        )
        closest_file = None if len(matches) == 0 else file_path.parent / matches[0]
        raise FileNotFoundError(
            {"missing_file": file_path, "closest_file_name": closest_file}
        )

    with open(file_path, "r") as f:
        data = f.read()

    return TCodeAST.model_validate_json(data)


class TCodeScriptBuilder:
    """Builder for TCode scripts."""

    def __init__(self, name: str, description: str | None = None) -> None:
        """Initialize a new TCode script builder with metadata."""
        self._labware_key_to_fleet_index: dict[str, int] = {}
        self._tool_key_to_robot_index: list[dict[str, int]] = []

        self.reset(name, description)

        self.default_path_type = PathType.SAFE
        self.default_trajectory_type = TrajectoryType.JOINT_SQUARE
        self.default_pipette_speed = 100.0  # uL/s

    def reset(self, name: str, description: str | None = None) -> None:
        """Set up the builder to write a new script."""
        metadata = Metadata(
            name=name,
            description=description,
            timestamp=0.0,  # Will be overwritten on call to emit()
            tcode_api_version=importlib.metadata.version("tcode_api"),
        )
        self.ast = TCodeAST(metadata=metadata, fleet=Fleet(), tcode=[])
        self._labware_key_to_fleet_index = {}
        self._tool_key_to_robot_index = []

    def set_up_from_file(self, file_path: pathlib.Path) -> None:
        """Load a TCode script from a file into the builder for modification."""
        self.ast = load_tcode_json_file(file_path)
        file_version = self.ast.metadata.tcode_api_version
        current_version = importlib.metadata.version("tcode_api")
        if file_version != current_version:
            _logger.warning(
                "Loaded TCode script was created with API version %s, current version is %s",
                file_version,
                current_version,
            )

    def emit(self) -> TCodeAST:
        """Return the current TCode script as an abstract syntax tree."""
        return self.ast.model_copy()

    def write_to_file(self, file_path: pathlib.Path, overwrite: bool = False) -> None:
        """Save the current TCode script to a file."""
        if file_path.is_file():
            if overwrite:
                _logger.info("Overwriting existing file %s", file_path)
            else:
                raise RuntimeError(
                    "File already exists. Use overwrite=True to overwrite."
                )

        self.ast.metadata.timestamp = time.time()

        with file_path.open("w") as file:
            file.write(self.ast.model_dump_json())

    def _labware_key_to_labware(self, labware_key: str) -> Labware:
        try:
            index = self._labware_key_to_fleet_index[labware_key]

        except KeyError:
            _logger.error(
                "Builder has no labware registered under key %s: %s",
                labware_key,
                self._labware_key_to_labware,
            )
            raise ValueError(labware_key)

        return self.ast.fleet.labware[index]

    def _tool_key_to_tool(self, tool_key: str) -> Tool:
        try:
            tool_key_to_tool = self._tool_key_to_robot_index[0]
            index = tool_key_to_tool[tool_key]

        except KeyError:
            _logger.error(
                "Builder has no tool registered under key %s: %s",
                tool_key,
                self._tool_key_to_robot_index,
            )
            raise ValueError(tool_key)

        if len(self.ast.fleet.robots) > 1:
            _logger.warning(
                "Assuming tool_key %s refers to 0th robot in fleet", tool_key
            )
        return self.ast.fleet.robots[0].tools[index]

    def _labware_specification_to_location(self, key: str, index: int) -> Location:
        """Turn builder's labware key and labware index into a TCode-compliant Location."""
        serial = self._labware_key_to_labware(key).serial
        return Location(type=LocationType.LABWARE_INDEX, data=(serial, index))

    # Construction Command Methods #

    def add_robot(self, robot: Robot) -> None:
        """Add a new robot to the targeted fleet."""
        if robot in self.ast.fleet.robots:
            _logger.error("Robot %s already exists in fleet %s", robot, self.ast.fleet)
            raise ValueError(robot)

        if len(robot.tools) > 0:
            raise NotImplementedError(
                "add_robot() doesn't support robots with tools. Use buoilder.add_tool() to add tools to a robot."
            )

        self.ast.fleet.robots.append(robot)
        self._tool_key_to_robot_index.append({})

    def add_labware(self, key: str, labware: Labware) -> None:
        """Add a new labware to the script."""
        # Check that key is unique
        if key in self._labware_key_to_fleet_index.keys():
            labware = self.ast.fleet.labware[self._labware_key_to_fleet_index[key]]
            _logger.error(
                "Builder already has labware registered with key %s: %s", key, labware
            )
            raise ValueError(key)

        # Check that labware.serial is unique
        serials = {labware.serial: labware for labware in self.ast.fleet.labware}
        try:
            duplicate_labware = serials[labware.serial]
            _logger.error(
                "Labware with serial %s already registered: %s",
                labware.serial,
                duplicate_labware,
            )
            raise ValueError(labware)

        except KeyError:
            pass  # No duplicate serial found

        # Register labware
        self._labware_key_to_fleet_index[key] = len(self.ast.fleet.labware)
        self.ast.fleet.labware.append(labware)

    def add_tool(self, key: str, robot_index: int, tool: Tool) -> None:
        """Add a new tool to the script."""
        # Check robot_index
        try:
            tool_key_to_index = self._tool_key_to_robot_index[robot_index]
            robot = self.ast.fleet.robots[robot_index]

        except KeyError:
            _logger.error(
                "Builder has no robot registered under index %s: %s",
                robot_index,
                self.ast.fleet.robots,
            )
            raise ValueError(robot_index)

        # Check that key is unique
        if key in tool_key_to_index.keys():
            tool = robot.tools[tool_key_to_index[key]]
            _logger.error(
                "Builder already has tool registered with key %s: %s", key, tool
            )
            raise ValueError(key)

        # Register tool
        tool_key_to_index[key] = len(robot.tools)
        robot.tools.append(tool)

    def add_command(self, command) -> None:
        """Add a new command to the TCode script."""
        self.ast.tcode.append(command)

    def goto_labware_index(self, labware_key: str, labware_index: int) -> None:
        """Wrapper for add_command(GOTO) that auto-fills default values."""
        location = self._labware_specification_to_location(labware_key, labware_index)
        command = GOTO(
            location=location,
            path_type=self.default_path_type,
            trajectory_type=self.default_trajectory_type,
        )
        self.add_command(command)

    def aspirate(self, volume: float, speed: float | None = None) -> None:
        """Wrapper for add_command(ASPIRATE) that auto-fills default values."""
        speed = speed if speed is not None else self.default_pipette_speed
        command = ASPIRATE(
            volume=ValueWithUnits(magnitude=volume, units="microliters"),
            speed=ValueWithUnits(magnitude=speed, units="microliters/second"),
        )
        self.add_command(command)

    def dispense(self, volume: float, speed: float | None = None) -> None:
        """Wrapper for add_command(DISPENSE) that auto-fills default values."""
        speed = speed if speed is not None else self.default_pipette_speed
        command = DISPENSE(
            volume=ValueWithUnits(magnitude=volume, units="microliters"),
            speed=ValueWithUnits(magnitude=speed, units="microliters/second"),
        )
        self.add_command(command)

    def get_tip(self, labware_key: str, labware_index: int) -> None:
        """Wrapper for add_command(GET_TIP) that auto-fills default values."""
        location = self._labware_specification_to_location(labware_key, labware_index)
        command = GET_TIP(location=location)
        self.add_command(command)

    def drop_tip(self, labware_key: str, labware_index: int) -> None:
        """Wrapper for add_command(GET_TIP) that auto-fills default values."""
        location = self._labware_specification_to_location(labware_key, labware_index)
        command = DROP_TIP(location=location)
        self.add_command(command)

    def get_tool(self, tool_key: str) -> None:
        """Wrapper for add_command(GET_TOOL) that auto-fills default values."""
        tool = self._tool_key_to_tool(tool_key)
        command = GET_TOOL(tool=tool)
        self.add_command(command)

    def drop_tool(self) -> None:
        """Wrapper for add_command(DROP_TOOL) that auto-fills default values."""
        command = DROP_TOOL()
        self.add_command(command)
