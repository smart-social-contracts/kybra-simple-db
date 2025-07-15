from kybra_simple_db import *  # noqa: E402


class StressTestEntity(Entity):
    __alias__ = "name"
    name = String(min_length=1, max_length=100)
    value = Integer()
