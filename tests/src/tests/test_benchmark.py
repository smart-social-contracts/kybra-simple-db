"""Benchmark tests measuring IC instruction costs for key Entity operations.

Uses ic.performance_counter(0) to get exact instruction counts before/after
each operation. Results are returned as strings so the external orchestrator
can parse and compare them.
"""

from kybra import ic
from tester import Tester

from kybra_simple_db import (
    Database,
    Entity,
    Integer,
    ManyToOne,
    OneToMany,
    String,
)


class BenchZone(Entity):
    name = String()
    description = String()
    land = ManyToOne("BenchLand", "zones")


class BenchLand(Entity):
    name = String()
    area = Integer()
    zones = OneToMany("BenchZone", "land")


def _measure(func):
    """Measure instruction cost of a callable."""
    before = ic.performance_counter(0)
    result = func()
    after = ic.performance_counter(0)
    return after - before, result


def _seed_entities(count):
    """Seed the DB with `count` Land+Zone pairs with relationships."""
    for i in range(count):
        land = BenchLand(name=f"Land_{i}", area=i * 100)
        zone = BenchZone(name=f"Zone_{i}", description=f"Desc_{i}")
        zone.land = land


class TestBenchmark:
    def _clear(self):
        Database.get_instance().clear()
        Entity._context.clear()

    def seed(self, count: str):
        """Seed DB with entity pairs. Returns instruction cost."""
        self._clear()
        count = int(count)
        cost, _ = _measure(lambda: _seed_entities(count))
        ic.print(f"BENCH_RESULT:seed:{count}:{cost}")

    def create_entity(self, count: str):
        """Measure cost of creating a single entity at given DB size."""
        self._clear()
        count = int(count)
        _seed_entities(count)
        idx = count
        cost, _ = _measure(
            lambda: BenchZone(name=f"Zone_{idx}", description=f"Desc_{idx}")
        )
        ic.print(f"BENCH_RESULT:create_entity:{count}:{cost}")

    def load_level1(self, count: str):
        """Measure cost of Entity.load(level=1) at given DB size."""
        self._clear()
        count = int(count)
        _seed_entities(count)
        zone_id = str(count)  # Last zone
        # Clear registry so we force a DB load
        Database.get_instance().clear_registry()
        cost, _ = _measure(lambda: BenchZone.load(zone_id, level=1))
        ic.print(f"BENCH_RESULT:load_level1:{count}:{cost}")

    def load_level3(self, count: str):
        """Measure cost of Entity.load(level=3) at given DB size."""
        self._clear()
        count = int(count)
        _seed_entities(count)
        zone_id = str(count)
        Database.get_instance().clear_registry()
        cost, _ = _measure(lambda: BenchZone.load(zone_id, level=3))
        ic.print(f"BENCH_RESULT:load_level3:{count}:{cost}")

    def deserialize_new_level1(self, count: str):
        """Measure cost of deserialize (new entity) with level=1 at given DB size."""
        self._clear()
        count = int(count)
        _seed_entities(count)
        idx = count + 900  # ID that doesn't exist
        record = {
            "_type": "BenchZone",
            "_id": str(idx),
            "name": f"NewZone_{idx}",
            "description": f"NewDesc_{idx}",
        }
        cost, _ = _measure(lambda: Entity.deserialize(record, level=1))
        ic.print(f"BENCH_RESULT:deserialize_new_level1:{count}:{cost}")

    def deserialize_new_level3(self, count: str):
        """Measure cost of deserialize (new entity) with level=3 at given DB size."""
        self._clear()
        count = int(count)
        _seed_entities(count)
        idx = count + 900
        record = {
            "_type": "BenchZone",
            "_id": str(idx),
            "name": f"NewZone_{idx}",
            "description": f"NewDesc_{idx}",
        }
        cost, _ = _measure(lambda: Entity.deserialize(record, level=3))
        ic.print(f"BENCH_RESULT:deserialize_new_level3:{count}:{cost}")

    def deserialize_existing_level1(self, count: str):
        """Measure cost of deserialize (existing entity, upsert) with level=1."""
        self._clear()
        count = int(count)
        _seed_entities(count)
        target_id = str(max(1, count))
        record = {
            "_type": "BenchZone",
            "_id": target_id,
            "name": f"Updated_{target_id}",
            "description": f"UpdatedDesc_{target_id}",
        }
        Database.get_instance().clear_registry()
        cost, _ = _measure(lambda: Entity.deserialize(record, level=1))
        ic.print(f"BENCH_RESULT:deserialize_existing_level1:{count}:{cost}")

    def deserialize_existing_level3(self, count: str):
        """Measure cost of deserialize (existing entity, upsert) with level=3."""
        self._clear()
        count = int(count)
        _seed_entities(count)
        target_id = str(max(1, count))
        record = {
            "_type": "BenchZone",
            "_id": target_id,
            "name": f"Updated_{target_id}",
            "description": f"UpdatedDesc_{target_id}",
        }
        Database.get_instance().clear_registry()
        cost, _ = _measure(lambda: Entity.deserialize(record, level=3))
        ic.print(f"BENCH_RESULT:deserialize_existing_level3:{count}:{cost}")

    def serialize(self, count: str):
        """Measure cost of Entity.serialize() at given DB size."""
        self._clear()
        count = int(count)
        _seed_entities(count)
        zone = BenchZone.load(str(max(1, count)), level=1)
        cost, _ = _measure(lambda: zone.serialize())
        ic.print(f"BENCH_RESULT:serialize:{count}:{cost}")

    def bulk_deserialize_level1(self, count: str):
        """Measure cost of deserializing 10 new entities with level=1."""
        self._clear()
        count = int(count)
        _seed_entities(count)
        records = [
            {
                "_type": "BenchZone",
                "_id": str(count + 900 + i),
                "name": f"Bulk_{i}",
                "description": f"BulkDesc_{i}",
            }
            for i in range(10)
        ]

        def do_bulk():
            for r in records:
                Entity.deserialize(r, level=1)

        cost, _ = _measure(do_bulk)
        ic.print(f"BENCH_RESULT:bulk_deserialize_level1:{count}:{cost}")

    def bulk_deserialize_level3(self, count: str):
        """Measure cost of deserializing 10 new entities with level=3."""
        self._clear()
        count = int(count)
        _seed_entities(count)
        records = [
            {
                "_type": "BenchZone",
                "_id": str(count + 900 + i),
                "name": f"Bulk_{i}",
                "description": f"BulkDesc_{i}",
            }
            for i in range(10)
        ]

        def do_bulk():
            for r in records:
                Entity.deserialize(r, level=3)

        cost, _ = _measure(do_bulk)
        ic.print(f"BENCH_RESULT:bulk_deserialize_level3:{count}:{cost}")


def run(test_name: str = None, test_var: str = None):
    tester = Tester(TestBenchmark)
    return tester.run_test(test_name, test_var)


if __name__ == "__main__":
    exit(run())
