"""Stress tests for kybra-simple-db to test performance under high load."""


try:
    from kybra import ic
except ImportError:
    class MockIC:
        def print(self, *args, **kwargs):
            print(*args, **kwargs)
    ic = MockIC()

from performance_utils import PerformanceTracker  # noqa: E402
from tester import Tester  # noqa: E402

from kybra_simple_db import *  # noqa: E402

SMALL_BATCH_SIZE = 100
MEDIUM_BATCH_SIZE = 500
LARGE_BATCH_SIZE = 1000
STRESS_BATCH_SIZE = 2000


class StressTestEntity(Entity):
    """Test entity for stress testing."""

    def __init__(self, name: str, value: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.value = value

    name = String(min_length=1, max_length=100)
    value = Integer()


class RelatedEntity(Entity):
    """Related entity for relationship stress testing."""

    def __init__(self, category: str, **kwargs):
        super().__init__(**kwargs)
        self.category = category

    category = String(min_length=1, max_length=50)


class TestStress:
    def setUp(self):
        """Reset database before each test."""
        Database.get_instance().clear()
        self.tracker = PerformanceTracker()

    def tearDown(self):
        """Clean up after each test."""
        if hasattr(self, "tracker"):
            self.tracker.print_metrics()

    def test_bulk_insertion_small(self):
        """Test bulk insertion of 100 records."""
        self._test_bulk_insertion(SMALL_BATCH_SIZE, "100 Records")

    def test_bulk_insertion_medium(self):
        """Test bulk insertion of 500 records."""
        self._test_bulk_insertion(MEDIUM_BATCH_SIZE, "500 Records")

    def test_bulk_insertion_large(self):
        """Test bulk insertion of 1k records."""
        self._test_bulk_insertion(LARGE_BATCH_SIZE, "1K Records")

    def test_bulk_insertion_stress(self):
        """Test bulk insertion of 2k records."""
        self._test_bulk_insertion(STRESS_BATCH_SIZE, "2K Records")

    def _test_bulk_insertion(self, count: int, test_name: str):
        """Helper method to test bulk insertion with specified count."""
        with self.tracker.track_operation(f"Bulk Insert {test_name}"):
            entities = []
            for i in range(count):
                entity = StressTestEntity(name=f"Entity_{i}", value=i)
                entities.append(entity)

        assert StressTestEntity.count() == count
        ic.print(f"Successfully inserted {count} entities")

    def test_query_performance_after_bulk_insert(self):
        """Test query performance after bulk insertion."""
        insert_count = SMALL_BATCH_SIZE
        with self.tracker.track_operation("Setup - Bulk Insert"):
            for i in range(insert_count):
                StressTestEntity(name=f"Entity_{i}", value=i % 1000)

        with self.tracker.track_operation("Query - Count"):
            count = StressTestEntity.count()
            assert count == insert_count

        with self.tracker.track_operation("Query - Load by ID"):
            for i in [1, insert_count // 4, insert_count // 2, insert_count - 1]:
                entity = StressTestEntity.load(str(i))
                assert entity is not None

        with self.tracker.track_operation("Query - Pagination"):
            page_size = 100
            total_loaded = 0
            from_id = 1
            while from_id <= insert_count:
                page = StressTestEntity.load_some(from_id, page_size)
                total_loaded += len(page)
                from_id += page_size
                if len(page) < page_size:
                    break

            ic.print(f"Loaded {total_loaded} entities through pagination")

    def test_relationship_stress(self):
        """Test relationship performance under stress."""
        main_count = 50
        related_count = 10

        with self.tracker.track_operation("Create Main Entities"):
            main_entities = []
            for i in range(main_count):
                entity = StressTestEntity(name=f"Main_{i}", value=i)
                main_entities.append(entity)

        with self.tracker.track_operation("Create Related Entities"):
            related_entities = []
            for i in range(related_count):
                entity = RelatedEntity(category=f"Category_{i}")
                related_entities.append(entity)

        with self.tracker.track_operation("Create Relationships"):
            for i, main_entity in enumerate(main_entities):
                for j in range(5):
                    related_idx = (i * 7 + j) % related_count
                    related_entity = related_entities[related_idx]
                    main_entity.add_relation(
                        "related_to", "main_entities", related_entity
                    )

        with self.tracker.track_operation("Query Relationships"):
            sample_entity = main_entities[0]
            relations = sample_entity.get_relations("related_to")
            assert len(relations) == 5

    def test_scaling_performance(self):
        """Test performance scaling with increasing data."""
        batch_sizes = [50, 100, 200]

        for batch_size in batch_sizes:
            Database.get_instance().clear()

            with self.tracker.track_operation(f"Scale Test - {batch_size} entities"):
                for i in range(batch_size):
                    StressTestEntity(name=f"Entity_{i}", value=i)

                count = StressTestEntity.count()
                assert count == batch_size

                for i in range(0, min(10, batch_size), 5):
                    entity = StressTestEntity.load(str(i + 1))
                    assert entity is not None

    def test_deletion_performance(self):
        """Test deletion performance with large datasets."""
        create_count = SMALL_BATCH_SIZE
        with self.tracker.track_operation("Setup for Deletion Test"):
            entities = []
            for i in range(create_count):
                entity = StressTestEntity(name=f"ToDelete_{i}", value=i)
                entities.append(entity)

        with self.tracker.track_operation("Bulk Deletion"):
            deleted_count = 0
            for i in range(0, len(entities), 2):
                entities[i].delete()
                deleted_count += 1

        remaining_count = StressTestEntity.count()
        expected_remaining = create_count - deleted_count
        assert remaining_count == expected_remaining
        ic.print(f"Deleted {deleted_count} entities, {remaining_count} remaining")


def run():
    tester = Tester(TestStress)
    return tester.run_tests()


if __name__ == "__main__":
    exit(run())
