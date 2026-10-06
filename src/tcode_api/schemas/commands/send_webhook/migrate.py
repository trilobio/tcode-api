from ...registry import Migrator, RawData


def migrate_v1_to_v2(data: RawData) -> RawData:
    """Migrate a SEND_WEBHOOK command from schema version 1 to 2.

    v2 introduces a required ``module_id``: a webhook is addressed to a module registered by
    ``ADD_MODULE``, and executes from that module's queue. v1 payloads name no module, and
    there is no way to infer which device a legacy webhook belonged to, so this migrator
    raises rather than guessing.
    """
    if "module_id" not in data:
        raise ValueError(
            "Cannot migrate SEND_WEBHOOK v1 to v2 automatically: v2 requires a 'module_id'. "
            "Register the target device with ADD_MODULE and address the webhook to it."
        )
    retval = {**data}
    retval["schema_version"] = 2
    return retval


MIGRATORS: dict[int, Migrator] = {
    2: migrate_v1_to_v2,
}
