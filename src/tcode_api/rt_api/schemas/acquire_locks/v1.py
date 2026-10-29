from typing import Literal

from tcode_api.schemas.base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1


class ACQUIRE_LOCKS(BaseSchemaVersionedModelV1):
    type: Literal["ACQUIRE_LOCKS"] = "ACQUIRE_LOCKS"
    schema_version: Literal[1] = 1

    robot_serials: list[str]
