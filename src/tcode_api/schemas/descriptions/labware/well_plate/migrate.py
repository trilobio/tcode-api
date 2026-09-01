from ....registry import Migrator, RawData, is_description_or_descriptor
from ...liddability import LiddabilityDescription, LiddabilityDescriptor
from ..lid import LidDescription, LidDescriptor
from ..lid.migrate import migrate_v3_to_v4 as migrate_lid_v3_to_v4


def migrate_v1_to_v2(data: RawData) -> RawData:
    """Migrate a WellPlateDescription or WellPlateDescriptor from schema version 1 to 2."""
    # No attribute changes — bump top-level schema_version and nested lid schema_version.
    retval = {
        **data,
    }
    retval["schema_version"] = 2
    if retval.get("lid") is not None:
        retval["lid"] = {**retval["lid"], "schema_version": 2}
    return retval


def migrate_v2_to_v3(data: RawData) -> RawData:
    """Migrate a WellPlateDescription or WellPlateDescriptor from schema version 2 to 3."""
    # No attribute changes — bump top-level schema_version and nested lid schema_version.
    retval = {
        **data,
    }
    retval["schema_version"] = 3
    if retval.get("lid") is not None:
        retval["lid"] = {**retval["lid"], "schema_version": 3}
    return retval


# Prior to tcode-api v1.42.0, `aceta` set a default pinch offset of 10mm in z...
# https://github.com/trilobio/aceta/blob/772760d53f35f5574e95f77dd40ed03ffcb6f9ba/tcode/tcode/resolver/create_labware.py#L94
_DEFAULT_PINCH_OFFSET_TRANSFORM: list[list[float]] = [
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.010],
    [0.0, 0.0, 0.0, 1.0],
]


def migrate_v3_to_v4(data: RawData) -> RawData:
    """Migrate a WellPlateDescription or WellPlateDescriptor from schema version 3 to 4."""
    # v4 adds the required `pinchable` field. Well plates are pinched (not lifted) when picked up
    # (see robot.actions.move_plate.pick_up_plate), so pre-v4 well plates backfill as
    # pinchable=True. The nested lid (if present) is migrated via its own v3->v4 migrator so the
    # default-backfill logic for Lid lives in one place.
    retval = {
        **data,
    }
    retval["schema_version"] = 4
    retval.setdefault("pinchable", True)
    retval.setdefault("pinch_offset_transform", _DEFAULT_PINCH_OFFSET_TRANSFORM)
    if retval.get("lid") is not None:
        retval["lid"] = migrate_lid_v3_to_v4(retval["lid"])
    return retval


def migrate_v4_to_v5(data: RawData) -> RawData:
    """Migrate a WellPlateDescription or WellPlateDescriptor from schema version 4 to 5.

    Note that NO descriptor migrates to "i don't care if a plate is liddable or not" (i.e.
    liddability.is_liddable=None). This drawback is because this function is unably to cheaply tell
    if incoming data is a Description or Descriptor, and so assumes it MUST provide a Liddability
    field.

    Migration logic assumes the following:
    - If a labware has a lid OR a lid_offset, it should have a populated liddability field.
    - If a labware has neither lid nor lid_offset, liddability.is_lidabble is False.
    """
    retval = {
        **data,
    }
    retval["schema_version"] = 5
    if "liddability" in retval:
        # If the liddability field is already present, we don't need to backfill it.
        pass
    else:
        lid_offset = retval.get("lid_offset", None)
        lid = retval.get("lid", None)
        all_lid_fields_are_none = lid_offset is None and lid is None
        if is_description_or_descriptor(
            LidDescription,
            LidDescriptor,
            retval,
        )[0]:
            LidDescription.model_validate(lid)
            retval["liddability"] = LiddabilityDescription(
                supports_lid=not all_lid_fields_are_none,
                lid_offset=lid_offset,
                lid=lid,
            ).model_dump()
        else:
            retval["liddability"] = LiddabilityDescriptor(
                supports_lid=None if all_lid_fields_are_none else True,
                lid_offset=lid_offset,
                lid=lid,
            ).model_dump()

    # Remove deprecated keys
    retval.pop("lid_offset", None)
    retval.pop("lid", None)
    return retval


MIGRATORS: dict[int, Migrator] = {
    2: migrate_v1_to_v2,
    3: migrate_v2_to_v3,
    4: migrate_v3_to_v4,
    5: migrate_v4_to_v5,
}
