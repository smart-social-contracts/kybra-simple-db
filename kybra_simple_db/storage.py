"""
Storage backends for Kybra Simple DB
"""

from abc import ABC, abstractmethod
from typing import Dict, Iterator, Optional, Tuple


class Storage(ABC):
    """Abstract base class for storage backends"""

    @abstractmethod
    def insert(self, key: str, value: str) -> None:
        """Insert a key-value pair into storage"""
        raise NotImplementedError

    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """Retrieve a value by key"""
        raise NotImplementedError

    @abstractmethod
    def remove(self, key: str) -> None:
        """Remove a key-value pair from storage"""
        raise NotImplementedError

    @abstractmethod
    def items(self) -> Iterator[Tuple[str, str]]:
        """Return all items in storage"""
        raise NotImplementedError

    @abstractmethod
    def __contains__(self, key: str) -> bool:
        """Check if key exists in storage"""
        raise NotImplementedError

    @abstractmethod
    def keys(self) -> Iterator[str]:
        """Return all keys in storage"""
        raise NotImplementedError


class MemoryStorage(Storage):
    """In-memory storage implementation using Python dictionary"""

    def __init__(self):
        self._data: Dict[str, str] = {}
        self._next_id: int = 1

    def insert(self, key: str, value: str) -> None:
        self._data[key] = value

    def get(self, key: str) -> Optional[str]:
        return self._data.get(key)

    def remove(self, key: str) -> None:
        if key in self._data:
            del self._data[key]
        else:
            raise KeyError(f"Key '{key}' not found in storage")

    def items(self) -> Iterator[Tuple[str, str]]:
        return iter(self._data.items())

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def clear(self) -> None:
        """Clear all data from storage"""
        self._data.clear()
        self._next_id = 1

    def keys(self) -> Iterator[str]:
        """Return all keys in storage"""
        return iter(self._data.keys())

    def get_next_id(self) -> int:
        """Get the next available ID and increment the counter"""
        current_id = self._next_id
        self._next_id += 1
        return current_id

# TODO: add Kybra persistance storage here