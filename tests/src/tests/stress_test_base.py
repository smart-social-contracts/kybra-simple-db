"""Base module for stress tests with shared utilities and entity definitions."""

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

# Constants for batch sizes
SMALL_BATCH_SIZE = 100
MEDIUM_BATCH_SIZE = 500
LARGE_BATCH_SIZE = 800
STRESS_BATCH_SIZE = 1200


class StressTestEntity(Entity):
    __alias__ = "name"
    name = String(min_length=1, max_length=100)
    value = Integer()


class RelatedEntity(Entity):
    category = String(min_length=1, max_length=50)


class StressTestBase:
    """Base class for all stress tests with common setup and teardown."""

    def setUp(self):
        """Reset database before each test."""
        self.tracker = PerformanceTracker()

    def tearDown(self):
        """Clean up after each test."""
        if hasattr(self, "tracker"):
            self.tracker.print_metrics()
