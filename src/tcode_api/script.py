"""Human-readable scripting wrapper for the TCode API."""

import datetime
import importlib.metadata
import logging
import pathlib
from difflib import get_close_matches
from typing import Iterable, Protocol, cast

import tcode_api.api as tc
from tcode_api.error import IdExistsError, IdNotFoundError
from tcode_api.utilities import generate_id

_logger = logging.getLogger(__name__)


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
        self.ast: tc.TCodeAST
        self.reset(name, description)

        self.default_path_type = tc.PathType.SAFE
        self.default_trajectory_type = tc.TrajectoryType.JOINT_SQUARE
        self.default_pipette_speed = 100.0  # uL/s

    # Input/output management methods #

    def reset(self, name: str | None = None, description: str | None = None) -> None:
        """Set up the builder to write a new script."""
        if name is None:
            if hasattr(self, "ast"):
                name = self.ast.metadata.name
            else:
                raise AssertionError(
                    "Cannot call reset() before __init__ with name=None"
                )
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
            file.write(self.ast.model_dump_json())

    # Private implementation methods #

    def _location_as_labware_index(
        self, labware_id: Id, index: int
    ) -> tc.LocationAsLabwareIndex:
        """Turn builder's labware key and labware index into a TCode-compliant Location."""
        self._find_labware_by_id(labware_id)  # Check that the labware exists
        return tc.LocationAsLabwareIndex(labware_id=labware_id, location_index=index)

    def _location_relative_to_labware(
        self, labware_id: Id, matrix: tc.Matrix
    ) -> tc.LocationRelativeToLabware:
        """Turn builder's labware key and matrix into a TCode-compliant Location."""
        self._find_labware_by_id(labware_id)  # Check that the labware exists
        return tc.LocationRelativeToLabware(labware_id=labware_id, matrix=matrix)

    def _find_model_by_id(
        self, model_id: Id, model_list: Iterable[ModelWithId]
    ) -> ModelWithId:
        """Return the model with the given id."""
        models = [model for model in model_list if model.id == model_id]
        _logger.debug(
            '{"model_id": %s, "models": %s, "matching_models": %s}',
            model_id,
            model_list,
            models,
        )
        match len(models):
            case 1:
                return models[0]
            case 0:
                raise IdNotFoundError(model_id)
            case _:
                raise AssertionError(
                    "Multiple models with the same id found. This should not happen."
                )

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

    def _find_pipette_tip_group_by_id(
        self, pipette_tip_group_id: Id
    ) -> tc.PipetteTipGroup:
        """Return the pipette tip group with the given id."""
        return cast(
            tc.PipetteTipGroup,
            self._find_model_by_id(pipette_tip_group_id, self.ast.pipette_tips),
        )

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

    def add_pipette_tip_group(self, pipette_tip_group: tc.PipetteTipGroup) -> None:
        try:
            discovered_model = self._find_pipette_tip_group_by_id(pipette_tip_group.id)
            _logger.error(
                "Pipette tip group with id %s already exists: %s",
                pipette_tip_group.id,
                discovered_model,
            )
            raise IdExistsError(pipette_tip_group.id)
        except IdNotFoundError:
            self.ast.pipette_tips.append(pipette_tip_group)

    # TCode command methods #

    def aspirate(self, volume: float, speed: float | None = None) -> None:
        """Wrapper for add_command(ASPIRATE) that auto-fills default values."""
        speed = speed if speed is not None else self.default_pipette_speed
        command = tc.ASPIRATE(
            volume=tc.ValueWithUnits(magnitude=volume, units="microliters"),
            speed=tc.ValueWithUnits(magnitude=speed, units="microliters/second"),
        )
        self.add_command(command)

    def calibrate_labware_height(
        self, labware_id: Id, matrix: tc.Matrix, persistent: bool = False
    ) -> None:
        """Wrapper for add_command(CALIBRATE_LABWARE_HEIGHT) that auto-fills default values."""
        location = self._location_relative_to_labware(labware_id, matrix)
        command = tc.CALIBRATE_LABWARE_HEIGHT(
            location=location,
            persistent=persistent,
        )
        self.add_command(command)

    def calibrate_labware_well_depth(
        self,
        labware_id: Id,
        labware_index: int,
        modify_all_wells: bool = False,
        persistent: bool = False,
    ) -> None:
        """Wrapper for add_command(CALIBRATE_LABWARE_WELL_DEPTH) that auto-fills default values."""
        location = self._location_as_labware_index(labware_id, labware_index)
        command = tc.CALIBRATE_LABWARE_WELL_DEPTH(
            location=location,
            modify_all_wells=modify_all_wells,
            persistent=persistent,
        )
        self.add_command(command)

    def calibrate_tool_for_probing(
        self,
        z_only: bool,
        persistent: bool = False,
    ) -> None:
        """Wrapper for add_command(CALIBRATE_TOOL_FOR_PROBING) that auto-fills default values."""
        command = tc.CALIBRATE_TOOL_FOR_PROBING(
            z_only=z_only,
            persistent=persistent,
        )
        self.add_command(command)

    def comment(self, text: str) -> None:
        """Wrapper for add_command(COMMENT)."""
        self.add_command(tc.COMMENTS(text=text))

    def discard_pipette_tip_group(self) -> None:
        """Wrapper for add_command(DISCARD_PIPETTE_TIP_GROUP)."""
        return self.add_command(tc.DISCARD_PIPETTE_TIP_GROUP())

    def dispense(self, volume: float, speed: float | None = None) -> None:
        """Wrapper for add_command(DISPENSE) that auto-fills default values."""
        speed = speed if speed is not None else self.default_pipette_speed
        command = tc.DISPENSE(
            volume=tc.ValueWithUnits(magnitude=volume, units="microliters"),
            speed=tc.ValueWithUnits(magnitude=speed, units="microliters/second"),
        )
        self.add_command(command)

    def goto_labware_index(self, labware_id: Id, labware_index: int) -> None:
        """Wrapper for add_command(GOTO) that auto-fills default values."""
        location = self._location_as_labware_index(labware_id, labware_index)
        command = tc.GOTO(
            location=location,
            path_type=self.default_path_type,
            trajectory_type=self.default_trajectory_type,
        )
        self.add_command(command)

    def pause(self) -> None:
        """Wrapper for add_command(PAUSE)."""
        self.add_command(tc.PAUSE())

    def pick_up_pipette_tip(self, labware_id: Id, labware_index: int) -> None:
        """Wrapper for add_command(PICK_UP_PIPETTE_TIP) that auto-fills default values."""
        location = self._location_as_labware_index(labware_id, labware_index)
        command = tc.PICK_UP_PIPETTE_TIP(location=location)
        self.add_command(command)

    def put_down_pipette_tip(self, labware_id: Id, labware_index: int) -> None:
        """Wrapper for add_command(PUT_DOWN_PIPETTE_TIP) that auto-fills default values."""
        location = self._location_as_labware_index(labware_id, labware_index)
        command = tc.PUT_DOWN_PIPETTE_TIP(location=location)
        self.add_command(command)

    def remove_plate_lid(
        self, labware_id: Id, storage_location: tc.Location | None = None
    ) -> None:
        """Wrapper for add_command(REMOVE_PLATE_LID) that auto-fills default values."""
        command = tc.REMOVE_PLATE_LID(
            plate_id=labware_id, storage_location=storage_location
        )
        self.add_command(command)

    def replace_plate_lid(self, labware_id: Id, lid_id: Id | None = None) -> None:
        """Wrapper for add_command(REPLACE_PLATE_LID) that auto-fills default values."""
        command = tc.REPLACE_PLATE_LID(plate_id=labware_id, lid_id=lid_id)
        self.add_command(command)

    def retrieve_pipette_tip_group(
        self, pipette_tip_group_id: str | None = None, make_new_group: bool = False
    ) -> None:
        """Wrapper for add_command(RETRIEVE_PIPETTE_TIP_GROUP) that auto-fills default values."""
        if make_new_group:
            if pipette_tip_group_id is None:
                pipette_tip_group_id = generate_id()
            self.add_pipette_tip_group(
                tc.PipetteTipGroup(
                    id=pipette_tip_group_id,
                    row_count=1,
                    column_count=1,
                )
            )

        else:
            if pipette_tip_group_id is None:
                raise ValueError(
                    "pipette_tip_group_id must be provided if make_new_group is False."
                )
            try:
                self._find_pipette_tip_group_by_id(pipette_tip_group_id)
            except IdNotFoundError:
                _logger.error(
                    "Pipette tip group with id %s does not exist.", pipette_tip_group_id
                )
                raise IdNotFoundError(pipette_tip_group_id)

        command = tc.RETRIEVE_PIPETTE_TIP_GROUP(id=pipette_tip_group_id)
        self.add_command(command)

    def return_pipette_tip_group(self) -> None:
        """Wrapper for add_command(RETURN_PIPETTE_TIP_GROUP)."""
        self.add_command(tc.RETURN_PIPETTE_TIP_GROUP())

    def retrieve_tool(self, tool_id: Id) -> None:
        """Wrapper for add_command(RETRIEVE_TOOL) that auto-fills default values."""
        tool = self._find_tool_by_id(tool_id)
        command = tc.RETRIEVE_TOOL(id=tool.id)
        self.add_command(command)

    def return_tool(self) -> None:
        """Wrapper for add_command(RETURN_TOOL) that auto-fills default values."""
        command = tc.RETURN_TOOL()
        self.add_command(command)

    def wait(self, duration: float) -> None:
        """Wrapper for add_command(WAIT) that auto-fills default values."""
        command = tc.WAIT(
            duration=tc.ValueWithUnits(magnitude=duration, units="seconds")
        )
        self.add_command(command)
