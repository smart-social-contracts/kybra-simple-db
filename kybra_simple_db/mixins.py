"""Mixins for adding functionality to database entities."""

from typing import Any, Dict, Optional

from .system_time import SystemTime


class TimestampedMixin:
    """Mixin that adds creation and update timestamps to entities."""

    def __init__(self):
        self._timestamp_created = 0
        self._timestamp_updated = 0
        self._creator = None
        self._updater = None
        self._owner = None

    def _update_timestamps(self, caller_id: Optional[str] = None) -> None:
        """Update timestamps and track who made the changes.

        Args:
            caller_id: ID of the user/process making the change
        """
        now = SystemTime.get_instance().get_time()
        if not self._timestamp_created:
            self._timestamp_created = now
            self._creator = caller_id
            self._owner = caller_id

        self._timestamp_updated = now
        self._updater = caller_id

    def set_owner(self, new_owner: str) -> None:
        """Set a new owner for this entity.

        Args:
            new_owner: ID of the new owner
        """
        self._owner = new_owner

    def check_ownership(self, caller_id: str) -> bool:
        """Check if the caller owns this entity.

        Args:
            caller_id: ID of the caller to check

        Returns:
            bool: True if caller owns the entity, False otherwise
        """
        return self._owner == caller_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert timestamps and ownership info to a dictionary.

        Returns:
            Dict containing the timestamp and ownership data
        """

        return {
            "timestamp_created": SystemTime.format_timestamp(self._timestamp_created),
            "timestamp_updated": SystemTime.format_timestamp(self._timestamp_updated),
            "creator": self._creator,
            "updater": self._updater,
            "owner": self._owner,
        }
