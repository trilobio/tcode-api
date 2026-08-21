"""CLI tool to execute TCode in a .tc file."""

import logging
import pathlib

import plac  # type: ignore [import-untyped]

import tcode_api.api as tc
from tcode_api.api import TCodeScript
from tcode_api.cli import (
    DEFAULT_SERVICER_URL,
    servicer_url_annotation,
)
from tcode_api.servicer import TCodeServicerClient

def prompt_accept_deck_layout(script: tc.TCodeScript) -> None:
    """Display deck layout and required tools from provided script and prompt user to accept before proceeding."""
    # Read deck layout
    layout_commands: list[tc.CREATE_LABWARE] = [
        cmd for cmd in script.commands if isinstance(cmd, tc.CREATE_LABWARE)
    ]
    tool_commands: list[tc.ADD_TOOL] = [
        cmd for cmd in script.commands if isinstance(cmd, tc.ADD_TOOL)
    ]
    print("The script requires the following:")
    print("Tools: -------------------")
    for tool_cmd in tool_commands:
        print(
            f"\t{tool_cmd.descriptor.type}: max_volume={getattr(tool_cmd.descriptor, 'max_volume', 'N/A')}"
        )
    print("Deck Layout: -------------------")
    for layout_cmd in layout_commands:
        holder = layout_cmd.holder
        if holder.type == "LabwareHolderName":
            assert isinstance(holder, tc.LabwareHolderName)  # mypy type narrowing
            try:
                labware_name = layout_cmd.description.named_tags['name']
            except KeyError:
                labware_name = "<no name>"
            try:
                model_name = layout_cmd.description.named_tags['model']
            except KeyError:
                model_name = "<no model>"
            print(f"\t{holder.name} | {layout_cmd.description.type:18} | {model_name:30} | {labware_name}")





    while True:
        ans = input("Continue? [Y|n]: ").lower()
        if ans in ["n", "no", "q", "quit", "stop", "exit"]:
            sys.exit(0)
        elif ans in ["", "y", "yes", "continue"]:
             return
        else:
            print(f"Bad entry {ans} not in ['y', 'n']")


@plac.annotations(
    file_path=plac.Annotation(".tc file to parse", type=pathlib.Path),
    servicer_url=servicer_url_annotation,
)
def main(file_path: pathlib.Path, servicer_url: str = DEFAULT_SERVICER_URL) -> None:
    """Load and execute a .tc file."""
    logger = logging.getLogger('tcode_api.servicer.client')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    with file_path.open() as io_object:
        file_text = io_object.read()

    script = TCodeScript.model_validate_json(file_text)
    prompt_accept_deck_layout(script)
    client = TCodeServicerClient(servicer_url=servicer_url)
    client.run_script(script)


if __name__ == "__main__":
    plac.call(main)
