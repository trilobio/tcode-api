from typing import Literal

from tcode_api.schemas.base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1


class RELEASE_LOCKS(BaseSchemaVersionedModelV1):
    type: Literal["RELEASE_LOCKS"] = "RELEASE_LOCKS"
    schema_version: Literal[1] = 1

    robot_serials: list[str]
