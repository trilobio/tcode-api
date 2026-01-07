import pathlib
import random
from dataclasses import dataclass

import plac  # type: ignore [import-untyped]

import tcode_api.api as tc

from tcode_api.cli import (
    DEFAULT_SERVICER_URL,
    servicer_url_annotation,
)
from tcode_api.servicer import TCodeServicerClient
from tcode_api.utilities import (
    generate_id,
    generate_tcode_script_from_protocol_designer,
    generate_new_tip_group_ids,
)


_tcode_out_annotation = plac.Annotation(
    help="Where to write generated .tc (defaults to <protocol>.tc)",
    abbrev="t",
    kind="option",
    type=pathlib.Path,
)

_cli_options_out_annotation = plac.Annotation(
    help=("Where to write Protocol Designer CLI options JSON (defaults to a temporary file)"),
    abbrev="o",
    kind="option",
    type=pathlib.Path,
)

_pnpm_annotation = plac.Annotation(
    help="Command used to invoke pnpm",
    kind="option",
    type=str,
)


def str_list_from_csv(input: str) -> list[str]:
    """Convert a comma-separated string to a list of strings."""
    if not input:
        return []
    return [item.strip() for item in input.split(",") if item.strip()]


_set_annotation = plac.Annotation(
    help=(
        "Override CLI option(s) (comma-separated). Example: --set useMC8P300=false "
        "or --set useMC8P300=false,otherOption=true"
    ),
    kind="option",
    type=str_list_from_csv,
)

_symbol_annotation = plac.Annotation(
    help=(
        "Symbol specs (comma-separated). Format: name:type:init:min:max. "
        "Example: --symbol numSteps:int:5:1:10 or --symbol k:float:0.2:0.1:0.9"
    ),
    kind="option",
    type=str_list_from_csv,
)

_iterator_symbol_annotation = plac.Annotation(
    help=(
        "If set, also pass an integer symbol to the protocol indicating the iteration. "
        "Value is 1-based (1..N). Example: --iterator-symbol iteration"
    ),
    abbrev="i",
    kind="option",
    type=str,
)


@dataclass(frozen=True)
class SymbolSpec:
    name: str
    type: str  # "int" | "float"
    init_value: float
    min_value: float
    max_value: float

    @staticmethod
    def parse(raw: str) -> "SymbolSpec":
        parts = [p.strip() for p in raw.split(":")]
        if len(parts) != 5:
            raise ValueError(
                "Invalid --symbol entry. Expected 'name:type:init:min:max'. " f"Got: {raw!r}"
            )

        name, symbol_type, init_str, min_str, max_str = parts
        symbol_type = symbol_type.lower()
        if symbol_type not in {"int", "float"}:
            raise ValueError(
                f"Invalid symbol type {symbol_type!r} for {name!r}. Expected 'int' or 'float'."
            )

        try:
            init_value = float(init_str)
            min_value = float(min_str)
            max_value = float(max_str)
        except ValueError as exc:
            raise ValueError(
                f"Invalid numeric value in --symbol entry: {raw!r}. "
                "Expected init/min/max to be numbers."
            ) from exc

        if min_value > max_value:
            raise ValueError(f"Invalid range for {name!r}: min={min_value} > max={max_value}")

        return SymbolSpec(
            name=name,
            type=symbol_type,
            init_value=init_value,
            min_value=min_value,
            max_value=max_value,
        )

    def format_value(self, value: float) -> str:
        if self.type == "int":
            return str(int(value))
        return str(float(value))

    def init_override(self) -> str:
        return f"{self.name}={self.format_value(self.init_value)}"

    def random_override(self, rng: random.Random) -> str:
        if self.type == "int":
            lo = int(self.min_value)
            hi = int(self.max_value)
            if lo > hi:
                raise ValueError(f"Invalid int range for {self.name!r} after casting: {lo}..{hi}")
            value = rng.randint(lo, hi)
            return f"{self.name}={value}"

        value = rng.uniform(self.min_value, self.max_value)
        return f"{self.name}={self.format_value(value)}"


@plac.annotations(
    protocol=("Path to Protocol Designer JSON (.tbw) protocol", "positional", None, pathlib.Path),
    protocol_designer_dir=(
        "Path to Protocol Designer directory containing CLI tools for TCode generation",
        "positional",
        None,
        pathlib.Path,
    ),
    tcode_out=_tcode_out_annotation,
    cli_options_out=_cli_options_out_annotation,
    set=_set_annotation,
    symbol=_symbol_annotation,
    iterator_symbol=_iterator_symbol_annotation,
    num_iterations=(
        "Number of iterations to run the optimizer on the protocol variables",
        "option",
        "n",
        int,
    ),
    servicer_url=servicer_url_annotation,
    pnpm=_pnpm_annotation,
)
def main(
    protocol: pathlib.Path,
    protocol_designer_dir: pathlib.Path,
    tcode_out: pathlib.Path | None = None,
    cli_options_out: pathlib.Path | None = None,
    set: list[str] | None = None,
    symbol: list[str] | None = None,
    iterator_symbol: str | None = None,
    num_iterations: int = 3,
    servicer_url: str = DEFAULT_SERVICER_URL,
    pnpm: str = "pnpm",
):
    if tcode_out is None:
        tcode_out = pathlib.Path("/tmp/output.tc")

    symbol_specs = [SymbolSpec.parse(s) for s in (symbol or [])]
    if iterator_symbol is not None:
        iterator_symbol = iterator_symbol.strip()
        if not iterator_symbol:
            raise ValueError("--iterator-symbol cannot be empty")
        if any(spec.name == iterator_symbol for spec in symbol_specs):
            raise ValueError(
                f"--iterator-symbol {iterator_symbol!r} conflicts with a --symbol spec of the same name"
            )
    rng = random.Random()

    def symbol_overrides_for_iteration(iteration_index: int) -> list[str] | None:
        overrides: list[str] = []

        if iterator_symbol is not None:
            # 0-based iteration counter so protocols can do `if (iteration == 0) ...`.
            overrides.append(f"{iterator_symbol}={iteration_index}")

        if not symbol_specs:
            return overrides or None
        if iteration_index == 0:
            overrides.extend(spec.init_override() for spec in symbol_specs)
            return overrides
        overrides.extend(spec.random_override(rng) for spec in symbol_specs)
        return overrides

    client = TCodeServicerClient(servicer_url=servicer_url)
    labware_id = generate_id()
    labware_deck_slot = ""
    robot_id = generate_id()
    gripper_id = generate_id()
    for iteration in range(num_iterations):
        is_first = iteration == 0

        # Do sensor reading in python here!

        iteration_symbol_overrides = symbol_overrides_for_iteration(iteration)
        script = generate_tcode_script_from_protocol_designer(
            protocol,
            protocol_designer_dir,
            tcode_out=tcode_out,
            cli_options_out=cli_options_out,
            set_overrides=set,
            symbol_overrides=iteration_symbol_overrides,
            pnpm=pnpm,
        )

        print(f"--- Iteration {iteration + 1} of {num_iterations} ---")
        if is_first:
            for cmd in script.commands:
                if isinstance(cmd, tc.ADD_ROBOT):
                    robot_id = cmd.id
                if isinstance(cmd, tc.ADD_LABWARE):
                    if cmd.descriptor.type == "WellPlate" and cmd.descriptor.grid is not None and cmd.descriptor.grid.row_count == 8 and cmd.descriptor.grid.column_count == 12:
                        labware_id = cmd.id
            for cmd in script.commands:
                if isinstance(cmd, tc.CREATE_LABWARE):
                    if cmd.description.type == "WellPlate" and cmd.description.grid.row_count == 8 and cmd.description.grid.column_count == 12:
                        print("Found labware deck slot: ", cmd.holder.name)
                        labware_deck_slot = cmd.holder.name

            # Make sure gripper is availiable!
            script.commands.append(
                tc.ADD_TOOL(robot_id=robot_id, id=gripper_id, descriptor=tc.GripperDescriptor())
            )
            client.run_script(script, clean_environment=True)
        else:
            # Remove any ADD_* and CREATE_LABWARE commands to avoid ID conflicts.
            script.commands = [
                cmd
                for cmd in script.commands
                if not isinstance(
                    cmd, (tc.ADD_LABWARE, tc.ADD_TOOL, tc.ADD_ROBOT, tc.CREATE_LABWARE)
                )
            ]
            script = generate_new_tip_group_ids(script)
            client.run_script(script, clean_environment=False)

        # Read plate
        plate_read_script = tc.TCodeScript.new(
            name=__file__,
            description=__doc__,
        )
        plate_read_script.commands.append(tc.RETRIEVE_TOOL(robot_id=robot_id, id=gripper_id))
        plate_read_script.commands.append(tc.PICK_UP_LABWARE(robot_id=robot_id, labware_id=labware_id))
        plate_read_script.commands.append(
            tc.PUT_DOWN_LABWARE(
                robot_id=robot_id,
                holder=tc.LabwareHolderName(
                    robot_id=robot_id,
                    name="DeckSlot_16",
                ),
            )
        )
        plate_read_script.commands.append(tc.PICK_UP_LABWARE(robot_id=robot_id, labware_id=labware_id))
        plate_read_script.commands.append(
            tc.PUT_DOWN_LABWARE(
                robot_id=robot_id,
                holder=tc.LabwareHolderName(
                    robot_id=robot_id,
                    name=labware_deck_slot,
                ),
            )
        )
        plate_read_script.commands.append(tc.RETURN_TOOL(robot_id=robot_id))
        client.run_script(plate_read_script, clean_environment=False)


if __name__ == "__main__":
    plac.call(main)
