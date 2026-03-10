from typing import Callable

from .v2 import migrate_v1_to_v2

MIGRATORS: dict[int, Callable] = {
    2: migrate_v1_to_v2,
}
