"""CLI tool to execute TCode in a .tc file."""

import logging
import pathlib

import plac  # type: ignore [import-untyped]

from tcode_api.api import TCodeScript
from tcode_api.cli import (
    DEFAULT_SERVICER_URL,
    servicer_url_annotation,
)
from tcode_api.servicer import TCodeServicerClient


@plac.annotations(
    file_path=plac.Annotation(".tc file to parse", type=pathlib.Path),
    servicer_url=servicer_url_annotation,
)
def main(file_path: pathlib.Path, servicer_url: str = DEFAULT_SERVICER_URL) -> None:
    """Load and execute a .tc file."""
    logger = logging.getLogger("tcode_api.servicer.client")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    with file_path.open() as io_object:
        file_text = io_object.read()

    script = TCodeScript.model_validate_json(file_text)
    client = TCodeServicerClient(servicer_url=servicer_url)
    client.run_script(script)


if __name__ == "__main__":
    plac.call(main)
