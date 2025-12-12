"""Various helpful components for creating command-line interfaces for TCode scripts."""

import pathlib

import plac  # type: ignore [import-untyped]

DEFAULT_SERVICER_URL = "http://localhost:8002"


def validate_servicer_url(value: str) -> str:
    """Validate that the servicer URL is well-formed.

    Args:
        value (str): The servicer URL to validate.

    Returns:
        str: The validated servicer URL.

    Raises:
        ValueError: If any of the following conditions aren't met:
            - The URL starts with "http://" or "https://".
    """
    if not value.startswith("http://") and not value.startswith("https://"):
        raise ValueError("Servicer URL must start with 'http://' or 'https://'")
    return value


servicer_url_annotation = plac.Annotation(
    help="Connect to the TCode servicer at this URL",
    abbrev="s",
    kind="option",
    type=validate_servicer_url,
)

output_file_path_annotation = plac.Annotation(
    "If set, write the generated TCode script to this file path",
    abbrev="o",
    kind="option",
    type=pathlib.Path,
)
