"""Developer script to migrate stored schema definitions (e.g. labware) to the current Tcode API version."""

import sys
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
        abbrev="v",
    ),
    check=plac.Annotation(
        "Fail if the committed generated files are out of date instead of rewriting them.",
        type=bool,
        kind="flag",
        abbrev="c",
    ),
)
def main(
    schema_dir: Path = DEFAULT_LABWARE_PATH, print_tb: bool = False, check: bool = False
) -> int:
    """Migrate stored schema definitions to the current Tcode API version.

    Reads every JSON file in ``schema_dir``, dispatching each independently by its own ``"type"``
    field -- the directory may contain a mix of schema kinds (e.g. ``tcode_labware/`` mixes
    labware descriptions with nested ``PipetteTip`` files). Each file is migrated to the current
    schema version and re-written in place.

    :param schema_dir: Directory of schema definitions to migrate.
    :param print_tb: Print full traceback on error (default: False)
    :param check: Fail if the committed generated files are out of date instead of rewriting

    :return: process exit code (0 = ok / written, 1 = stale in check mode, 2 = failed migration of 1+
        files).
    """
    if not schema_dir.exists():
        raise FileNotFoundError(f"Schema directory {schema_dir} does not exist.")

    schema_io = SchemaIO(schema_dir=schema_dir)
    failures: dict[Path, str] = {}
    migrated_count = 0
    check_map: dict[Path, tuple[str, str]] = {}
    for schema_file in sorted(schema_dir.glob("*.json")):
        existing = schema_file.read_text(encoding="utf-8")
        try:
            schema = schema_io.load(schema_file)
        except Exception as err:  # report and continue, don't abort the batch
            if print_tb:
                failures[schema_file] = traceback.format_exc()
            else:
                failures[schema_file] = repr(err)
            continue

        schema_io.write(schema_file, schema)
        generated = schema_file.read_text(encoding="utf-8")
        check_map[schema_file] = (existing, generated)
        migrated_count += 1

    print(f"Migrated {migrated_count} schema file(s).")
    if failures:
        print(f"{len(failures)} file(s) could not be auto-migrated -- fix these by hand:")
        for path, message in failures.items():
            print(f"  {path.name}: {message}")
        return 2

    if check:
        stale_files = [
            path for path, (existing, generated) in check_map.items() if existing != generated
        ]
        if stale_files:
            print(f"{len(stale_files)} file(s) are stale -- regenerate with:")
            print("    uv run python scripts/migrate_schemas.py")
            for path in stale_files:
                print(f"  {path.name}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(plac.call(main))
