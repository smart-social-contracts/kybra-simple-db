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
    _current_time: Optional[int] = None

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
        if self._current_time is not None:
            return self._current_time
        return int(time.time() * 1000)  # Convert to milliseconds

    def set_time(self, timestamp: int) -> None:
        """Set a fixed time.

        Args:
            timestamp: Time in milliseconds since epoch
        """
        self._current_time = timestamp

    def clear_time(self) -> None:
        """Clear the fixed time and revert to using real system time."""
        self._current_time = None

    def advance_time(self, milliseconds: int) -> None:
        """Advance the current time by the specified number of milliseconds.

        If no fixed time is set, this will set the time to current time + milliseconds.

        Args:
            milliseconds: Number of milliseconds to advance
        """
        current = self.get_time()
        self.set_time(current + milliseconds)

    @staticmethod
    def format_timestamp(timestamp: int) -> str:
        """Format a timestamp as a human-readable string.

        Args:
            timestamp: Time in milliseconds since epoch

        Returns:
            Formatted string like "2025-02-09 15:26:27 (1739111587)"
        """
        if not timestamp:
            return "Never"
        dt = datetime.fromtimestamp(timestamp / 1000)
        return f"{dt} ({timestamp})"
