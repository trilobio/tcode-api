"""Developer script to migrate stored schema definitions (e.g. labware) to the current Tcode API version."""

import traceback
from pathlib import Path

import plac  # type: ignore [import-untyped]

from tcode_api.utilities import DEFAULT_LABWARE_PATH, SchemaIO


@plac.annotations(
    schema_dir=plac.Annotation(
        "Directory of schema definitions to migrate",
        type=Path,
    ),
    print_tb=plac.Annotation(
        "Print full traceback on error (default: False)",
        type=bool,
        kind="flag",
    ),
)
def main(schema_dir: Path = DEFAULT_LABWARE_PATH, print_tb: bool = False) -> None:
    """Migrate stored schema definitions to the current Tcode API version.

    Reads every JSON file in ``schema_dir``, dispatching each independently by its own ``"type"``
    field -- the directory may contain a mix of schema kinds (e.g. ``tcode_labware/`` mixes
    labware descriptions with nested ``PipetteTip`` files). Each file is migrated to the current
    schema version and re-written in place.

    :param schema_dir: Directory of schema definitions to migrate.
    :param print_tb: Print full traceback on error (default: False)
    """
    if not schema_dir.exists():
        raise FileNotFoundError(f"Schema directory {schema_dir} does not exist.")

    schema_io = SchemaIO(schema_dir=schema_dir)
    failures: dict[Path, str] = {}
    migrated_count = 0
    for schema_file in sorted(schema_dir.glob("*.json")):
        try:
            schema = schema_io.load(schema_file)
        except Exception as err:  # report and continue, don't abort the batch
            if print_tb:
                failures[schema_file] = traceback.format_exc()
            else:
                failures[schema_file] = repr(err)
            continue

        schema_io.write(schema_file, schema)
        migrated_count += 1

    print(f"Migrated {migrated_count} schema file(s).")
    if failures:
        print(f"{len(failures)} file(s) could not be auto-migrated -- fix these by hand:")
        for path, message in failures.items():
            print(f"  {path.name}: {message}")


if __name__ == "__main__":
    plac.call(main)
