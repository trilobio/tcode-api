# Agent instructions

## Schema migrations: how to evolve a versioned schema

Every schema under [src/tcode_api/schemas/](src/tcode_api/schemas/) is **versioned**. Once a `vN.py` file has been released (i.e. it appears in any tagged version of `tcode-api`), its contents are part of the wire format and must be treated as immutable. Do **not** mutate `vN.py` to add, remove, or change the type of fields, change a parent class, or otherwise alter how a payload of that version validates.

The reference implementation for a schema bump is commit [`dbf4732`](https://github.com/trilobio/tcode-api/commit/dbf4732b24014bc2c94c239a0b6061828ba5dc5c) (`Add Speed to MOVE_TO_LOCATION`). Follow exactly the same pattern any time you change the shape of an existing schema.

### When this applies

Any of the following is a **schema change** and requires a version bump:

- Adding a required field.
- Removing a field.
- Renaming a field.
- Changing a field's type (including narrowing or widening, e.g. `str` → `Literal[...]`).
- Changing the parent class in a way that adds or removes fields (e.g. moving from `BaseTCodeCommand` to `BaseRobotSpecificTCodeCommand` because `robot_id` is now required).
- Changing a default in a way that affects validation of older data.

Adding a **new optional field with a default** that does not affect validation of older payloads is wire-compatible and does not strictly require a bump, but a bump is still preferred when the new field meaningfully changes behavior, so that `compat.py` documents which `tcode-api` version began honoring it.

### Step-by-step pattern (illustrated by `dbf4732`)

For a schema named `FOO` currently at `vN`:

1. **Leave [vN.py](src/tcode_api/schemas/.../foo/v1.py) untouched.** Existing serialized payloads must continue to deserialize against the unchanged class.
2. **Add `vN+1.py`** next to it. Define the new class (same Python class name as the previous version — e.g. `FOO`, not `FOO_V2`) inheriting from the appropriate base, with `schema_version: Literal[N+1] = N+1`.
3. **Re-point `latest.py`** to import from `.vN+1` instead of `.vN`.
4. **Add a migrator** in `migrate.py`:

   ```python
   def migrate_v1_to_v2(data: RawData) -> RawData:
       retval = {**data}
       retval["schema_version"] = 2
       # set defaults for new fields, or raise if the migration cannot be performed
       return retval

   MIGRATORS: dict[int, Callable] = {2: migrate_v1_to_v2}
   ```

   If the new field is required and has no sensible default, the migrator should `raise` with a clear message rather than silently fabricating a value.

5. **Register the bump in [src/tcode_api/api/compat.py](src/tcode_api/api/compat.py)** under a new `tcode-api` semantic version key inside `increments`, e.g.:
   ```python
   "v1.39.0": {
       "FOO": 2,
   },
   ```
6. **Bump `version` in [pyproject.toml](pyproject.toml)** to match the new compat entry.
7. **Add a regression test** in [tests/test_api/test_compat.py](tests/test_api/test_compat.py) exercising `migrate_data_to_latest` for the new bump.

### Anti-patterns

Do **not**:

- Mutate an existing `vN.py` to change its parent class, add required fields, or otherwise change its validation behavior. This silently breaks every client and stored script that holds a `vN` payload.
- Add a required field with no migration entry, on the assumption that callers will "just update".
- Change `latest.py` without adding the corresponding `vN+1.py` and migrator.
- Add a new compat entry without bumping `pyproject.toml`, or vice versa.

### Additions to `BaseTCodeCommand` / shared base classes

A field added to a shared base class (e.g. [src/tcode_api/schemas/commands/base.py](src/tcode_api/schemas/commands/base.py)) affects **every** subclass schema. Treat this as a schema change for each affected subclass:

- If the field is optional with a default, you may add it without bumping every subclass, but record the addition in `compat.py` (under a new version key, listing each affected schema at its new version) so the change is traceable.
- If the field is required, you must add a `vN+1.py` for every affected schema, with migrators, exactly as above. Doing this in a single PR is acceptable and expected.

## After code changes

After finishing a set of edits and before committing or handing off for review:

1. `uv run ruff format`
2. `uv run ruff check`
3. `uv run mypy ./`
4. `uv run python -m unittest discover tests`

Tests in this repo are written against the standard library `unittest`
framework (see e.g. `tests/test_api/test_compat.py`,
`tests/test_schemas/test_serialization.py`). Use `unittest.TestCase` /
`unittest.IsolatedAsyncioTestCase` and run them with `python -m unittest`
rather than `pytest` (the project does not depend on `pytest`).

If any step fails, fix the reported issues before committing. If a failure is unrelated or blocked, say so explicitly.
