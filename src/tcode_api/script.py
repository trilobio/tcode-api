"""Human-readable scripting wrapper for the TCode API."""

import datetime
import importlib.metadata
import logging
import pathlib
from difflib import get_close_matches
from typing import Iterable, Protocol, cast

import tcode_api.api as tc
from tcode_api.error import IdExistsError, IdNotFoundError

_logger = logging.getLogger("tcode_api.script")


def load_tcode_json_file(file_path: pathlib.Path) -> tc.TCodeAST:
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

    return tc.TCodeAST.model_validate_json(data)


class ModelWithId(Protocol):
    id: str


Id = str


class TCodeScriptBuilder:
    """Builder for TCode scripts."""

    def __init__(self, name: str, description: str | None = None) -> None:
        """Initialize a new TCode script builder with metadata."""
        self.reset(name, description)

        self.default_path_type = tc.PathType.SAFE
        self.default_trajectory_type = tc.TrajectoryType.JOINT_SQUARE
        self.default_pipette_speed = 100.0  # uL/s

    # Input/output management methods #

    def reset(self, name: str, description: str | None = None) -> None:
        """Set up the builder to write a new script."""
        metadata = tc.Metadata(
            name=name,
            description=description,
            timestamp=datetime.datetime.now().isoformat(),
            tcode_api_version=importlib.metadata.version("tcode_api"),
        )
        self.ast = tc.TCodeAST(metadata=metadata, fleet=tc.Fleet(), tcode=[])

    def emit(self) -> tc.TCodeAST:
        """Return the current TCode script as an abstract syntax tree."""
        return self.ast.model_copy()

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

    def write_to_file(self, file_path: pathlib.Path, overwrite: bool = False) -> None:
        """Save the current TCode script to a file."""
        if file_path.is_file():
            if overwrite:
                _logger.info("Overwriting existing file %s", file_path)
            else:
                raise RuntimeError(
                    "File already exists. Use overwrite=True to overwrite."
                )

        self.ast.metadata.timestamp = datetime.datetime.now().isoformat()

        with file_path.open("w") as file:
            file.write(self.ast.model_dump_json(indent=4))

    # Private implementation methods #

    def _labware_specification_to_location(
        self, labware_id: Id, index: int
    ) -> tc.LocationAsLabwareIndex:
        """Turn builder's labware key and labware index into a TCode-compliant Location."""
        self._find_labware_by_id(labware_id)  # Check that the labware exists
        return tc.LocationAsLabwareIndex(data=(labware_id, index))

    def _find_model_by_id(
        self, model_id: Id, model_list: Iterable[ModelWithId]
    ) -> ModelWithId:
        """Return the model with the given id."""
        models = [model for model in model_list if model.id == model_id]
        match len(models):
            case 0:
                _logger.error("No matching model in %s", model_list)
            case 1:
                return models[0]
            case _:
                _logger.error(
                    "Multiple models with id %s in %s: %s",
                    model_id,
                    model_list,
                    models,
                )

        raise IdNotFoundError(model_id)

    def _find_labware_by_id(self, labware_id: Id) -> tc.Labware:
        """Return the labware with the given id."""
        return cast(
            tc.Labware, self._find_model_by_id(labware_id, self.ast.fleet.labware)
        )

    def _find_tool_by_id(self, tool_id: Id) -> tc.Tool:
        """Return the tool with the given id."""
        return cast(
            tc.Tool,
            self._find_model_by_id(
                tool_id, [t for r in self.ast.fleet.robots for t in r.tools]
            ),
        )

    def _find_robot_by_id(self, robot_id: Id) -> tc.Robot:
        """Return the robot with the given id."""
        return cast(tc.Robot, self._find_model_by_id(robot_id, self.ast.fleet.robots))

    # Component registration methods #

    def add_command(self, command) -> None:
        """Add a new command to the TCode script."""
        self.ast.tcode.append(command)

    def add_labware(self, labware: tc.Labware) -> None:
        """Add a new labware to the script."""
        try:
            discovered_model = self._find_labware_by_id(labware.id)
            _logger.error(
                "Labware with id %s already exists: %s", labware.id, discovered_model
            )
            raise IdExistsError(labware.id)
        except IdNotFoundError:
            pass

        self.ast.fleet.labware.append(labware)

    def add_robot(self, robot: tc.Robot) -> None:
        """Add a new robot to the targeted fleet."""
        if len(robot.tools) > 0:
            raise NotImplementedError(
                "add_robot() doesn't support robots with tools. Use buoilder.add_tool() to add tools to a robot."
            )
        try:
            discovered_model = self._find_robot_by_id(robot.id)
            _logger.error(
                "Robot with id %s already exists: %s", robot.id, discovered_model
            )
            raise IdExistsError(robot.id)
        except IdNotFoundError:
            self.ast.fleet.robots.append(robot)

    def add_tool(self, robot_id: Id, tool: tc.Tool) -> None:
        """Add a new tool to the script on a specific robot."""
        try:
            discovered_model = self._find_tool_by_id(tool.id)
            _logger.error(
                "Tool with id %s already exists: %s", tool.id, discovered_model
            )
            raise IdExistsError(tool.id)
        except IdNotFoundError:
            robot = self._find_robot_by_id(robot_id)
            robot.tools.append(tool)

    # TCode command methods #

    def aspirate(self, volume: float, speed: float | None = None) -> None:
        """Wrapper for add_command(ASPIRATE) that auto-fills default values."""
        speed = speed if speed is not None else self.default_pipette_speed
        command = tc.ASPIRATE(
            volume=tc.ValueWithUnits(magnitude=volume, units="microliters"),
            speed=tc.ValueWithUnits(magnitude=speed, units="microliters/second"),
        )
        self.add_command(command)

    def calibrate_fts_noise_floor(self, axes: tc.Axes, snr: float) -> None:
        """Wrapper for add_command(CALIBRATE_FTS_NOISE_FLOOR)."""
        self.add_command(tc.CALIBRATE_FTS_NOISE_FLOOR(axes=axes, snr=snr))

    def comment(self, text: str) -> None:
        """Wrapper for add_command(COMMENT)."""
        self.add_command(tc.COMMENTS(text=text))

    def pause(self) -> None:
        """Wrapper for add_command(PAUSE)."""
        self.add_command(tc.PAUSE())

    def put_down_pipette_tip(self, labware_id: Id, labware_index: int) -> None:
        """Wrapper for add_command(PUT_DOWN_PIPETTE_TIP) that auto-fills default values."""
        location = self._labware_specification_to_location(labware_id, labware_index)
        command = tc.PUT_DOWN_PIPETTE_TIP(location=location)
        self.add_command(command)

    def return_tool(self) -> None:
        """Wrapper for add_command(RETURN_TOOL) that auto-fills default values."""
        command = tc.RETURN_TOOL()
        self.add_command(command)

    def dispense(self, volume: float, speed: float | None = None) -> None:
        """Wrapper for add_command(DISPENSE) that auto-fills default values."""
        speed = speed if speed is not None else self.default_pipette_speed
        command = tc.DISPENSE(
            volume=tc.ValueWithUnits(magnitude=volume, units="microliters"),
            speed=tc.ValueWithUnits(magnitude=speed, units="microliters/second"),
        )
        self.add_command(command)

    def pick_up_pipette_tip(self, labware_id: Id, labware_index: int) -> None:
        """Wrapper for add_command(PICK_UP_PIPETTE_TIP) that auto-fills default values."""
        location = self._labware_specification_to_location(labware_id, labware_index)
        command = tc.PICK_UP_PIPETTE_TIP(location=location)
        self.add_command(command)

    def remove_plate_lid(
        self, plate_id: Id, location_node_id: str | None = None
    ) -> None:
        """Wrapper for add_command(REMOVE_PLATE_LID) that auto-fills default values."""
        storage_location = (
            tc.LocationAsNodeId(data=location_node_id) if location_node_id else None
        )
        command = tc.REMOVE_PLATE_LID(
            plate_id=plate_id, storage_location=storage_location
        )
        self.add_command(command)

    def replace_plate_lid(self, plate_id: Id, lid_id: Id | None = None) -> None:
        """Wrapper for add_command(REPLACE_PLATE_LID) that auto-fills default values."""
        command = tc.REPLACE_PLATE_LID(plate_id=plate_id, lid_id=lid_id)
        self.add_command(command)

    def retrieve_tool(self, tool_id: Id) -> None:
        """Wrapper for add_command(RETRIEVE_TOOL) that auto-fills default values."""
        tool = self._find_tool_by_id(tool_id)
        command = tc.RETRIEVE_TOOL(id=tool.id)
        self.add_command(command)

    def goto_labware_index(self, labware_id: Id, labware_index: int) -> None:
        """Wrapper for add_command(GOTO) that auto-fills default values."""
        location = self._labware_specification_to_location(labware_id, labware_index)
        command = tc.GOTO(
            location=location,
            path_type=self.default_path_type,
            trajectory_type=self.default_trajectory_type,
        )
        self.add_command(command)

    def probe(
        self, node_id: str, backoff_distance: float, speed_fraction: float
    ) -> None:
        """Wrapper for add_command(PROBE) that auto-fills default values."""
        location = tc.LocationAsNodeId(data=node_id)
        command = tc.PROBE(
            location=location,
            backoff_distance=tc.ValueWithUnits(
                magnitude=backoff_distance, units="millimeters"
            ),
            speed_fraction=speed_fraction,
        )
        self.add_command(command)

    def reset_fts(self) -> None:
        """Wrapper for add_command(RESET_FTS)."""
        self.add_command(tc.RESET_FTS())
