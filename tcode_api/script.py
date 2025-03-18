"""Human-readable scripting wrapper for the TCode API."""

import datetime
import importlib.metadata
import logging
import pathlib
from difflib import get_close_matches

from tcode_api.api import (
    GOTO,
    Fleet,
    Labware,
    Location,
    Metadata,
    PathType,
    Robot,
    TCodeAST,
    TrajectoryType,
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
        self.reset(name, description)

        self.default_path_type = PathType.SAFE
        self.default_trajectory_type = TrajectoryType.JOINT_SQUARE

    def reset(self, name: str, description: str | None = None) -> None:
        """Set up the builder to write a new script."""
        metadata = Metadata(
            name=name,
            description=description,
            timestamp=0.0,  # Will be overwritten on call to emit()
            tcode_api_version=importlib.metadata.version("tcode_api"),
        )
        self.ast = TCodeAST(metadata=metadata, fleet=Fleet(), tcode=[])

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

    def emit(self, file_path: pathlib.Path, overwrite: bool = False) -> None:
        """Save the current TCode script to a file."""
        if file_path.is_file():
            if overwrite:
                _logger.info("Overwriting existing file %s", file_path)
            else:
                raise RuntimeError(
                    "File already exists. Use overwrite=True to overwrite."
                )

        self.ast.metadata.timestamp = datetime.datetime()

        with file_path.open("w") as file:
            file.write(self.ast.model_dump())

    # Construction Command Methods #

    def add_robot(self, robot: Robot) -> None:
        """Add a new robot to the targeted fleet."""
        if robot in self.ast.fleet.robots:
            _logger.error("Robot %s already exists in fleet %s", robot, self.ast.fleet)
            raise ValueError(robot)

        self.ast.fleet.robots.append(robot)

    def add_labware(self, labware: Labware) -> None:
        """Add a new labware to the script."""
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

        self.ast.fleet.labware.append(labware)

    def add_command(self, command) -> None:
        """Add a new command to the TCode script."""
        self.ast.tcode.append(command)

    def goto_labware_index(self, labware_index: int) -> None:
        """Helpful wrapper for add_command(GOTO) that auto-fills many default values."""
        command = GOTO(
            location=Location(data=labware_index),
            path_type=self.default_path_type,
            trajectory_type=self.default_trajectory_type,
        )
        self.add_command(command)
