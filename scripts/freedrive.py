"""freedrive - Put a robot in teach mode to move it somewhere."""

import plac  # type: ignore [import-untyped]

import tcode_api.api as tc
from tcode_api.cli import (
    DEFAULT_SERVICER_URL,
    servicer_url_annotation,
)
from tcode_api.servicer import TCodeServicerClient
from tcode_api.utilities import generate_id


@plac.annotations(
    servicer_url=servicer_url_annotation,
)
def main(
    servicer_url: str = DEFAULT_SERVICER_URL,
) -> None:
    """CLI for the freedrive script. See module docstring for full documentation."""
    script = tc.TCodeScript.new(
        name=__file__,
        description=__doc__,
    )

    robot_id = generate_id()
    script.commands.append(tc.ADD_ROBOT(id=robot_id, descriptor=tc.RobotDescriptor()))
    client = TCodeServicerClient(servicer_url=servicer_url)
    client.run_script(script)
    client.teach_point(robot_id)


if __name__ == "__main__":
    plac.call(main)
