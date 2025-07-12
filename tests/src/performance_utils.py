import os
import time
from contextlib import contextmanager
from typing import Any, Callable, Dict

import psutil


class PerformanceTracker:
    """Utility class for tracking performance metrics during tests."""

    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.metrics = {}

    @contextmanager
    def track_operation(self, operation_name: str):
        """Context manager to track execution time and memory usage."""
        initial_memory = self.process.memory_info().rss / 1024 / 1024
        start_time = time.time()

        try:
            yield
        finally:
            end_time = time.time()
            final_memory = self.process.memory_info().rss / 1024 / 1024

            self.metrics[operation_name] = {
                "execution_time_seconds": end_time - start_time,
                "initial_memory_mb": initial_memory,
                "final_memory_mb": final_memory,
                "memory_delta_mb": final_memory - initial_memory,
            }

    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return self.metrics.copy()

    def print_metrics(self):
        """Print formatted metrics to console."""
        print("\n" + "=" * 60)
        print("PERFORMANCE METRICS")
        print("=" * 60)
        for operation, metrics in self.metrics.items():
            print(f"\n{operation}:")
            print(f"  Execution Time: {metrics['execution_time_seconds']:.3f} seconds")
            print(
                f"  Memory Usage: {metrics['initial_memory_mb']:.1f} MB -> {metrics['final_memory_mb']:.1f} MB"
            )
            print(f"  Memory Delta: {metrics['memory_delta_mb']:+.1f} MB")
        print("=" * 60)
