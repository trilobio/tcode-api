import pathlib

import plac  # type: ignore [import-untyped]

from tcode_api.cli import (
    DEFAULT_SERVICER_URL,
    servicer_url_annotation,
)
from tcode_api.servicer import TCodeServicerClient
from tcode_api.utilities import generate_tcode_script_from_protocol_designer


_tcode_out_annotation = plac.Annotation(
    help="Where to write generated .tc (defaults to <protocol>.tc)",
    abbrev="t",
    kind="option",
    type=pathlib.Path,
)

_cli_options_out_annotation = plac.Annotation(
    help=("Where to write Protocol Designer CLI options JSON (defaults to a temp file)"),
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


_create_cli_options_annotation = plac.Annotation(
    help="If set, generate cli-options JSON before generating TCode",
    abbrev="c",
    kind="flag",
)

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
        "Override symbol(s) (comma-separated). Example: --symbol numSteps=5 "
        "or --symbol numSteps=5,otherSymbol=123"
    ),
    kind="option",
    type=str_list_from_csv,
)


@plac.annotations(
    protocol=("Path to Protocol Designer JSON (.tbw) protocol", "positional", None, pathlib.Path),
    protocol_designer_dir=(
        "Path to Protocol Designer directory containing CLI tools for TCode generation",
        "positional",
        None,
        pathlib.Path,
    ),
    cli_options_out=_cli_options_out_annotation,
    create_cli_options=_create_cli_options_annotation,
    set=_set_annotation,
    symbol=_symbol_annotation,
    servicer_url=servicer_url_annotation,
    pnpm=_pnpm_annotation,
)
def main(
    protocol: pathlib.Path,
    protocol_designer_dir: pathlib.Path,
    cli_options_out: pathlib.Path | None = None,
    create_cli_options: bool = False,
    set: list[str] | None = None,
    symbol: list[str] | None = None,
    servicer_url: str = DEFAULT_SERVICER_URL,
    pnpm: str = "pnpm",
):
    script = generate_tcode_script_from_protocol_designer(
        protocol,
        protocol_designer_dir,
        tcode_out=pathlib.Path("/tmp/output.tc"),
        cli_options_out=cli_options_out,
        set_overrides=set,
        symbol_overrides=symbol,
        pnpm=pnpm,
    )
    print("Generated TCode: /tmp/output.tc")

    client = TCodeServicerClient(servicer_url=servicer_url)
    client.run_script(script, clean_environment=True)


if __name__ == "__main__":
    plac.call(main)
