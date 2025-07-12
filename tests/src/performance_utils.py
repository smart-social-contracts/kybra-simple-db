import os
import time
from contextlib import contextmanager
from typing import Any, Dict

from kybra import ic


class PerformanceTracker:
    """Utility class for tracking performance metrics during IC tests."""

    def __init__(self):
        self.metrics = {}

    @contextmanager
    def track_operation(self, operation_name: str):
        """Context manager to track execution time in IC environment."""
        start_time = time.time()

        try:
            yield
        finally:
            end_time = time.time()

            self.metrics[operation_name] = {
                "execution_time_seconds": end_time - start_time
            }

    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return self.metrics.copy()

    def print_metrics(self):
        """Print formatted metrics to IC console."""
        ic.print("=" * 60)
        ic.print("PERFORMANCE METRICS")
        ic.print("=" * 60)
        for operation, metrics in self.metrics.items():
            ic.print(f"{operation}:")
            ic.print(f"  Execution Time: {metrics['execution_time_seconds']:.3f} seconds")
        ic.print("=" * 60)
