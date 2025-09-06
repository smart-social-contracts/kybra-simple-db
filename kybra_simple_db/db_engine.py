"""
Core database engine implementation
"""

import json
import time
from typing import Any, Dict, List, Optional, Tuple

from kybra_simple_logging import get_logger

from .storage import MemoryStorage, Storage

logger = get_logger(__name__)


class Database:
    """Main database class providing high-level operations"""

    _instance = None
    _audit_enabled = False

    @classmethod
    def get_instance(cls) -> "Database":
        if not cls._instance:
            cls._instance = cls.init(audit_enabled=True)
        return cls._instance

    @classmethod
    def init(
        cls,
        audit_enabled: bool = False,
        db_storage: Storage = None,
        db_audit: Storage = None,
    ) -> "Database":
        if cls._instance:
            raise RuntimeError("Database instance already exists")
        cls._instance = cls(audit_enabled, db_storage, db_audit)
        return cls._instance

    def __init__(
        self,
        audit_enabled: bool = False,
        db_storage: Storage = None,
        db_audit: Storage = None,
    ):
        self._db_storage = db_storage if db_storage else MemoryStorage()
        self._audit_enabled = audit_enabled
        self._db_audit = None
        if self._audit_enabled:
            self._db_audit = db_audit if db_audit else MemoryStorage()

        if self._db_audit:
            self._db_audit.insert("_min_id", "0")
            self._db_audit.insert("_max_id", "0")

            logger.debug(
                f"Audit database initialized with {len(list(self._db_audit.items()))} items"
            )

        self._entity_types = {}

    def clear(self):
        keys = list(self._db_storage.keys())
        for key in keys:
            self._db_storage.remove(key)

        if not self._db_audit:
            return

        keys = list(self._db_audit.keys())
        for key in keys:
            self._db_audit.remove(key)

        self._db_audit.insert("_min_id", "0")
        self._db_audit.insert("_max_id", "0")

    def _audit(self, op: str, key: str, data: Any) -> None:
        if self._db_audit and self._audit_enabled:
            timestamp = int(time.time() * 1000)
            id = self._db_audit.get("_max_id")
            logger.debug(f"Audit: Recording {op} operation with ID {id}")
            self._db_audit.insert(str(id), json.dumps([op, timestamp, key, data]))
            self._db_audit.insert("_max_id", str(int(id) + 1))

    def save(self, type_name: str, id: str, data: dict) -> None:
        """Store the data under the given key

        Args:
            type_name: Type of the entity
            id: ID of the entity
            data: Data to store
        """
        key = f"{type_name}@{id}"
        self._db_storage.insert(key, json.dumps(data))
        self._audit("save", key, data)

    def load(self, type_name: str, id: str) -> Optional[dict]:
        """Load and return the data associated with the key

        Args:
            type_name: Type of the entity
            id: ID of the entity

        Returns:
            Dict if found, None otherwise
        """
        key = f"{type_name}@{id}"
        data = self._db_storage.get(key)
        if data:
            return json.loads(data)
        return None

    def delete(self, type_name: str, entity_id: str) -> None:
        """Delete the data associated with the key

        Args:
            type_name: Type of the entity
            id: ID of the entity
        """
        logger.debug(f"Database: Deleting entity {type_name}@{entity_id}")
        key = f"{type_name}@{entity_id}"
        data = self._db_storage.get(key)
        self._db_storage.remove(key)
        self._audit("delete", key, data)
        logger.debug(f"Database: Deleted entity {type_name}@{entity_id}")

    def update(self, type_name: str, id: str, field: str, value: Any) -> None:
        """Update a specific field in the stored data

        Args:
            type_name: Type of the entity
            id: ID of the entity
            field: Field to update
            value: New value
        """
        data = self.load(type_name, id)
        if data:
            data[field] = value
            self.save(type_name, id, data)
            self._audit("update", f"{type_name}@{id}", data)

    def get_all(self) -> Dict[str, Any]:
        """Return all stored data"""
        return {k: json.loads(v) for k, v in self._db_storage.items()}

    def register_entity_type(self, type_obj):
        """Register an entity type with the database.

        Args:
            type_obj: Type object to register
        """
        logger.debug(
            f"Registering type {type_obj.__name__} with bases {[b.__name__ for b in type_obj.__bases__]}"
        )
        self._entity_types[type_obj.__name__] = type_obj

    def is_subclass(self, type_name, parent_type):
        """Check if a type is a subclass of another type.

        Args:
            type_name: Name of the type to check
            parent_type: Parent type to check against

        Returns:
            bool: True if type_name is a subclass of parent_type
        """
        type_obj = self._entity_types.get(type_name)
        logger.debug(f"Type check: {type_name} -> {parent_type.__name__}")
        return type_obj and issubclass(type_obj, parent_type)

    def dump_json(self, pretty: bool = False) -> str:
        """Dump the entire database as a JSON string.

        Args:
            pretty: If True, format the JSON with indentation for readability

        Returns:
            JSON string containing all database data organized by type
        """
        result = {}
        for key in self._db_storage.keys():
            if key.startswith("_"):  # Skip internal keys
                continue
            try:
                type_name, id = key.split("@")
                if type_name not in result:
                    result[type_name] = {}
                result[type_name][id] = json.loads(self._db_storage.get(key))
            except (ValueError, json.JSONDecodeError):
                continue  # Skip invalid entries

        if pretty:
            return json.dumps(result, indent=2)
        return json.dumps(result)

    def raw_dump_json(self, pretty: bool = False) -> str:
        """Dump the raw contents of the storage as a JSON string.

        Args:
            pretty: If True, format the JSON with indentation for readability

        Returns:
            A JSON string representation of the raw storage contents
        """
        result = {}
        for key in self._db_storage.keys():
            result[key] = self._db_storage.get(key)
        if pretty:
            return json.dumps(result, indent=2)
        return json.dumps(result)

    def get_audit(
        self, id_from: Optional[int] = None, id_to: Optional[int] = None
    ) -> Dict[str, str]:
        """Get audit log entries between the specified IDs"""
        if not self._db_audit:
            return {}

        id_from = id_from or int(self._db_audit.get("_min_id"))
        id_to = id_to or int(self._db_audit.get("_max_id"))

        ret = {}
        for id in range(id_from, id_to):
            id_str = str(id)
            entry = self._db_audit.get(id_str)
            if entry:
                ret[id_str] = json.loads(entry)
        return ret
