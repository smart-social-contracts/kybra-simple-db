"""System time management for the database."""

import time
from datetime import datetime
from typing import Optional


class SystemTime:
    """Manages system time for the database.

    This class allows setting a fixed time for testing or synchronizing
    time across different systems. If no time is set, it uses the real
    system time.
    """

    _instance = None
    _current_time_ms: Optional[int] = None

    def __init__(self):
        if SystemTime._instance is not None:
            raise RuntimeError("Use SystemTime.get_instance() instead")
        SystemTime._instance = self

    @classmethod
    def get_instance(cls) -> "SystemTime":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_time(self) -> int:
        """Get the current time.

        If a fixed time is set, returns the fixed time,
        otherwise returns the real system time.

        Returns:
            int: Current time in milliseconds
        """
        if self._current_time_ms is not None:
            return self._current_time_ms
        return int(time.time() * 1000)  # Convert to milliseconds

    def set_time(self, timestamp: int) -> None:
        """Set a fixed time.

        Args:
            timestamp: Time in milliseconds since epoch
        """
        self._current_time_ms = timestamp

    def clear_time(self) -> None:
        """Clear the fixed time and revert to using real system time."""
        self._current_time_ms = None

    def advance_time(self, milliseconds: int) -> None:
        """Advance the current time by the specified number of milliseconds.

        If no fixed time is set, this will set the time to current time + milliseconds.

        Args:
            milliseconds: Number of milliseconds to advance
        """
        current = self.get_time()
        print(
            f"Advancing time by {milliseconds} ms (current: {current}) = {current + milliseconds}"
        )
        self.set_time(current + milliseconds)

    @staticmethod
    def format_timestamp(timestamp: int) -> str:
        """Format a timestamp as a human-readable string.

        Args:
            timestamp: Time in milliseconds since epoch

        Returns:
            Formatted string like "2025-02-09 15:26:27.123"
        """
        if not timestamp:
            return "None"
        dt = datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S.%f")[
            :-3
        ]
        return f"{dt}"

    def print(self) -> str:
        return self.format_timestamp(self.get_time())
