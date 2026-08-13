---
name: Tcode API Schema Migration
description: Generates the boilerplate necessary for migration of Tcode API schema(s) between semantic versions. Use whenever the user either a. changes a class in a `base/<model>/v#.py` file under tcode_api/schemas, b. adds a new `v#.py` file to an existing schema structure, or c. asks for a change to a schema in the Tcode API.
---

## Overview

Every schema under [src/tcode_api/schemas/](src/tcode_api/schemas/) is **versioned**. Once a `vN.py` file has been released (i.e. it appears in any tagged version of `tcode-api`), its contents are part of the wire format and must be treated as immutable. Do **not** mutate `vN.py` to add, remove, or change the type of fields, change a parent class, or otherwise alter how a payload of that version validates.

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
2. **Add `vN+1.py`** next to it. The docstring of this file must describe in bullet-points the changes from the `vN.py` file. Define the new class (same Python class name as the previous version — e.g. `FOO`, not `FOO_V2`) inheriting from the appropriate base, with `schema_version: Literal[N+1] = N+1`.
3. **Re-point `latest.py`** to import from `.vN+1` instead of `.vN`.
4. **Add a migrator** in `migrate.py`:

   ```python
   def migrate_v1_to_v2(data: RawData) -> RawData:
       retval = {**data}
       retval["schema_version"] = 2
       # set defaults for new fields, or raise if the migration cannot be performed
       return retval


   MIGRATORS: dict[int, Migrator] = {2: migrate_v1_to_v2}
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
- Mutate a shared `base/<model>/vK.py` class in place, for the same reason as mutating a leaf `vN.py` — every leaf schema that inherits from it is affected at once. See "Shared base classes" below.
- Import a base class via a `latest`-style indirection from inside a frozen `vN.py` file. Always import the exact, hardcoded base version.

### Shared base classes (`base/`)

Classes like `BaseTCodeCommand` or `BaseLabwareDescription` aren't leaf schemas themselves — they're inherited by many leaf schemas to tie together attributes that represent the same logical concern (e.g. every command has a `type` discriminator; every labware description has `x_length`/`y_length`/`z_length`). They live under a `base/` directory next to the schemas that use them, e.g. [src/tcode_api/schemas/commands/base/](src/tcode_api/schemas/commands/base/), [src/tcode_api/schemas/descriptions/labware/base/](src/tcode_api/schemas/descriptions/labware/base/).

**Structure**, mirroring leaf schemas but with two deliberate differences (see below):

```
commands/base/
  tcode_command/
    __init__.py          # empty
    v1.py                 # class BaseTCodeCommandV1(...)
  robot_specific_tcode_command/
    __init__.py
    v1.py                 # class BaseRobotSpecificTCodeCommandV1(BaseTCodeCommandV1, ...)
```

- **One subdirectory per independently-versioned model**, named after the class (snake_case, `Base` prefix dropped — e.g. `BaseTCodeCommand` → `tcode_command/`). **Do not bundle unrelated models in one file** just because they happen to live in the same conceptual area (that was the original bug: `BaseConfiguredModel` and `BaseSchemaVersionedModel` shared one file and one version number despite having no reason to change together). **Exception**: a `Description`/`Descriptor` pair for the same entity (e.g. `BaseLabwareDescription` + `BaseLabwareDescriptor`) stays in one model directory and one `vN.py`, since they represent the same entity and always bump in lockstep.
- **Class names carry the version suffix**: `BaseTCodeCommandV1`, `BaseTCodeCommandV2`, etc. — unlike leaf schemas, which keep the same class name across versions (`FOO`, not `FOO_V2`).
- **No `latest.py`.** This is the critical difference, not a simplification — see below.
- **No `migrate.py`, no `compat.py` registration, no `pyproject.toml` bump.** Base classes aren't independently migratable entities; they don't represent a wire payload on their own, only concrete leaf schemas do. Migrating a leaf schema that inherits fields from a base is still driven entirely by that leaf's own `migrate.py`, exactly as in the main pattern above.

**Why no `latest.py`:** the whole point of freezing `vN.py` is that once released, its *entire* class hierarchy is pinned by literal, hardcoded reference — not just its own fields. `latest.py` is a pointer that gets repointed later (that's its job for leaf schemas — `lid/latest.py` moves from `.v1` to `.v3` over time). If a leaf schema's frozen `vN.py` imported a base class via `from ..base.tcode_command.latest import BaseTCodeCommandV2` instead of `from ..base.tcode_command.v2 import BaseTCodeCommandV2`, then the day someone ships `base/tcode_command/v3.py` and repoints `latest.py` at it, every leaf schema that imported through `latest` would silently inherit a different parent shape — the exact bug this skill exists to prevent, just laundered through one more layer of indirection. **Every leaf `vN.py` must import its base class(es) by explicit, hardcoded version, always** (`from ..base.<model>.v1 import <Class>V1`, never `.latest`).

**When a base class needs a new field:**

1. Leave the existing `base/<model>/vK.py` untouched.
2. Add `base/<model>/vK+1.py` with the new class (`<Class>VK+1`), inheriting from the previous version's class.
3. Update the specific leaf schemas that need the new field: they get their own new `vN+1.py` (per the main pattern above) that imports and inherits from `base/<model>/vK+1.py` instead of the prior base version. Leaf schemas that don't need the change keep pointing at the old base version — a base version bump does **not** force every consumer to move.
4. Each affected leaf schema's own migrator, `compat.py` entry, and `pyproject.toml` bump follow the main pattern exactly, as if the field had been added directly to that leaf schema. If the same required field with no universal sensible default is being backfilled across multiple leaf schemas' migrators, check for existing signals elsewhere in the wider codebase (e.g. other repos' construction call sites, docstrings describing real-world behavior) for a *per-schema* default, and confirm with the user before committing to it if it's not unambiguous for every affected schema.
5. **Check for out-of-band data**, not just wire payloads that flow through `migrate_data_to_latest`. Static fixture data validated directly against `.latest` (e.g. JSON files loaded via `TypeAdapter.validate_python`, with no `schema_version` key and no migration step) will fail validation the moment a leaf's `latest.py` moves past the version they were written against, and needs the new field backfilled by hand, file by file — `uv run runner.py test` will surface these as `pydantic.ValidationError`s if you check test output rather than assuming success.

## After code changes

After finishing a set of edits and before committing or handing off for review:

1. `uv run runner.py format`
2. `uv run runner.py lint`
3. `uv run runner.py test`

If any step fails, fix the reported issues before committing. If a failure is unrelated or blocked, say so explicitly.
