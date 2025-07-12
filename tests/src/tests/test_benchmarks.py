"""Benchmark tests for kybra-simple-db performance analysis."""

import sys
import os
import time
import statistics

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from performance_utils import PerformanceTracker
from tester import Tester
from kybra_simple_db import *


class BenchmarkEntity(Entity):
    """Entity for benchmarking tests."""

    def __init__(self, name: str, data: str = "", **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.data = data

    name = String(min_length=1, max_length=100)
    data = String(max_length=1000)


class TestBenchmarks:
    def setUp(self):
        """Reset database before each test."""
        Database.get_instance().clear()
        self.tracker = PerformanceTracker()

    def tearDown(self):
        """Clean up after each test."""
        if hasattr(self, "tracker"):
            self.tracker.print_metrics()

    def test_single_operation_benchmarks(self):
        """Benchmark individual operations multiple times for statistical analysis."""
        iterations = 100

        creation_times = []
        for i in range(iterations):
            start_time = time.time()
            entity = BenchmarkEntity(name=f"Bench_{i}", data="x" * 100)
            end_time = time.time()
            creation_times.append(end_time - start_time)

        loading_times = []
        for i in range(1, iterations + 1):
            start_time = time.time()
            entity = BenchmarkEntity.load(str(i))
            end_time = time.time()
            loading_times.append(end_time - start_time)
            assert entity is not None

        print(f"\nEntity Creation Benchmark ({iterations} iterations):")
        print(f"  Average: {statistics.mean(creation_times) * 1000:.3f} ms")
        print(f"  Median: {statistics.median(creation_times) * 1000:.3f} ms")
        print(f"  Min: {min(creation_times) * 1000:.3f} ms")
        print(f"  Max: {max(creation_times) * 1000:.3f} ms")

        print(f"\nEntity Loading Benchmark ({iterations} iterations):")
        print(f"  Average: {statistics.mean(loading_times) * 1000:.3f} ms")
        print(f"  Median: {statistics.median(loading_times) * 1000:.3f} ms")
        print(f"  Min: {min(loading_times) * 1000:.3f} ms")
        print(f"  Max: {max(loading_times) * 1000:.3f} ms")

    def test_scaling_benchmark(self):
        """Test how performance scales with data size."""
        test_sizes = [100, 500, 1000, 5000, 10000]

        for size in test_sizes:
            Database.get_instance().clear()

            with self.tracker.track_operation(f"Scale Test - {size} entities"):
                for i in range(size):
                    BenchmarkEntity(name=f"Scale_{i}", data="x" * 50)

                start_time = time.time()
                BenchmarkEntity.count()
                count_time = time.time() - start_time

                start_time = time.time()
                instances = BenchmarkEntity.instances()
                instances_time = time.time() - start_time

                start_time = time.time()
                page = BenchmarkEntity.load_some(1, 100)
                pagination_time = time.time() - start_time

                print(f"\nScale {size} - Query Performance:")
                print(f"  Count(): {count_time * 1000:.3f} ms")
                print(f"  Instances(): {instances_time * 1000:.3f} ms")
                print(f"  Pagination: {pagination_time * 1000:.3f} ms")

                assert BenchmarkEntity.count() == size
                assert len(instances) == size
                assert len(page) == min(100, size)

    def test_concurrent_operations_simulation(self):
        """Simulate concurrent-like operations by interleaving different operations."""
        with self.tracker.track_operation("Concurrent Simulation"):
            entities = []

            for i in range(1000):
                entity = BenchmarkEntity(name=f"Concurrent_{i}", data=f"data_{i}")
                entities.append(entity)

                if i % 10 == 0 and i > 0:
                    BenchmarkEntity.count()

                    if entities:
                        random_idx = i % len(entities)
                        loaded = BenchmarkEntity.load(entities[random_idx]._id)
                        assert loaded is not None

                    page = BenchmarkEntity.load_some(max(1, i - 50), 10)
                    assert len(page) <= 10


def run():
    tester = Tester(TestBenchmarks)
    return tester.run_tests()


if __name__ == "__main__":
    exit(run())
