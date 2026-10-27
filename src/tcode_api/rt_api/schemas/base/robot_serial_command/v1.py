from abc import ABC

from tcode_api.schemas.base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1
from tcode_api.schemas.common.docs import TypeField


class BaseRobotSerialCommandV1(BaseSchemaVersionedModelV1, ABC):
    type: TypeField
    robot_serial: str
