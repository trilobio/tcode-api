"""Human-readable scripting wrapper for the TCode API."""

import datetime
import importlib.metadata
import logging
import pathlib
from difflib import get_close_matches

import tcode_api.api as tc

_logger = logging.getLogger(__name__)


def load_tcode_json_file(file_path: pathlib.Path) -> tc.TCodeScript:
    """Load a TCode script from a json file."""
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

    return tc.TCodeScript.model_validate_json(data)


Id = str


class TCodeScriptBuilder:
    """Builder for TCode scripts."""

    def __init__(self, name: str, description: str | None = None) -> None:
        """Initialize a new TCode script builder with metadata."""
        self.script: tc.TCodeScript
        self.reset(name, description)

        self.default_path_type = tc.PathType.SAFE
        self.default_trajectory_type = tc.TrajectoryType.JOINT_SQUARE
        self.default_pipette_speed = 100.0  # uL/s

    def add_command(self, command: tc.TCode) -> None:
        """Add a new command to the TCode script."""
        self.script.commands.append(command)

    def emit(self) -> tc.TCodeScript:
        """Return the current TCode script as an abstract syntax tree."""
        return self.script.model_copy()

    def reset(self, name: str | None = None, description: str | None = None) -> None:
        """Set up the builder to write a new script."""
        if name is None:
            if hasattr(self, "script"):
                name = self.script.metadata.name
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
        self.script = tc.TCodeScript(metadata=metadata, commands=[])

    def set_up_from_file(self, file_path: pathlib.Path) -> None:
        """Load a TCode script from a file into the builder for modification."""
        self.script = load_tcode_json_file(file_path)
        file_version = self.script.metadata.tcode_api_version
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

        self.script.metadata.timestamp = datetime.datetime.now().isoformat()
        with file_path.open("w") as file:
            file.write(self.script.model_dump_json(indent=4))
