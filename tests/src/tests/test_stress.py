"""Stress tests for kybra-simple-db to test performance under high load."""

try:
    from kybra import ic
except ImportError:

    class MockIC:
        def print(self, *args, **kwargs):
            print(*args, **kwargs)

    ic = MockIC()

from tester import Tester  # noqa: E402

from kybra_simple_db import *  # noqa: E402

from .stress_test_base import StressTestEntity

BATCH_SIZE = 100


class TestStress:
    def test_bulk_insertion_and_load_small(self):
        """Test bulk insertion of 100 records."""
        self._test_bulk_insertion(BATCH_SIZE, "100 Records")

    def _test_bulk_insertion(self, count: int, test_name: str):
        """Helper method to test bulk insertion with specified count."""

        actual_count = StressTestEntity.count()

        for i in range(count):
            v = i + actual_count
            StressTestEntity(name=f"Entity_{v}", value=v)

        actual_count = StressTestEntity.count() - actual_count
        if actual_count == count:
            ic.print(
                f"Successfully inserted {count} entities. Total entities = {actual_count}"
            )
        else:
            raise Exception(
                "Expected %d entities inserted, instead got %d" % (count, actual_count)
            )

    def test_query_performance_after_bulk_insert(self):
        name = "Entity_%s" % (StressTestEntity.count() - 1)
        ic.print("Name lookup: name = %s" % name)
        entity = StressTestEntity[name]
        ic.print("Name lookup: entity = %s" % entity.to_dict())
        assert entity is not None


def run(test_name: str = None, test_var: str = None):
    tester = Tester(TestStress)
    return tester.run_tests()


if __name__ == "__main__":
    exit(run())
