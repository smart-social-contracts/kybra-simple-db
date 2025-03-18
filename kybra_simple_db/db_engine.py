"""
Core database engine implementation
"""

import json
import logging
import time
from pprint import pformat
from typing import Any, Dict, List, Optional, Tuple

from .storage import MemoryStorage, Storage

logger = logging.getLogger(__name__)


class Database:
    """Main database class providing high-level operations"""

    _instance = None

    def __init__(self, db_storage: Storage = None, db_audit: Optional[Storage] = None):
        self._db_storage = db_storage or MemoryStorage()
        self._db_audit = db_audit
        self._entity_types = {}  # Map of type names to type objects

        if db_audit and not db_audit.get("_min_id"):
            db_audit.insert("_min_id", "0")
            db_audit.insert("_max_id", "0")

    def _audit(self, op: str, key: str, data: Any) -> None:
        if self._db_audit:
            timestamp = int(time.time() * 1000)
            id = self._db_audit.get("_max_id")
            self._db_audit.insert(
                str(id), json.dumps([op, timestamp, key, data])
            )  # TODO: just store in audit the diff
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
        key = f"{type_name}@{entity_id}"
        if key in self._db_storage:
            data = self._db_storage.get(key)
            self._audit("delete", key, data)
            self._db_storage.remove(key)

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
        logger.debug(f"Checking if {type_name} is subclass of {parent_type.__name__}")
        logger.debug(f"Found type object: {type_obj}")
        if type_obj:
            logger.debug(f"Bases: {[b.__name__ for b in type_obj.__bases__]}")
        return type_obj and issubclass(type_obj, parent_type)

    # TODO: `dump_json`` and `raw_dump_json` should not parse the values (which are JSON strings) but rather compose
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
        raw_data = self._db_storage._data
        if pretty:
            return json.dumps(raw_data, indent=2)
        return json.dumps(raw_data)

    @classmethod
    def get_instance(cls) -> "Database":
        """Get the singleton instance of the database.

        Returns:
            Database: The singleton instance

        Raises:
            RuntimeError: If no instance has been created yet
        """
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

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
                ret[id_str] = entry
        return ret


class Entity:
    """Base class for database entities with relationship support"""

    _ID_PARAM_NAME = "id"  # `id` cannot be changed
    _SEPARATOR = "@"
    _id_counters: Dict[str, int] = {}
    _context = set()
    _db_storage = MemoryStorage()
    _db_audit = MemoryStorage()

    def __init__(self, entity_type: str, relations: Dict = None, **kwargs):
        self.entity_type = entity_type
        self.entity_id: Optional[int] = None  # No ID assigned until saved
        for key, value in kwargs.items():
            self.__dict__[key] = value
        self.relations = relations.copy() if relations else {}
        self.__class__._context.add(self)

    def key(self) -> str:
        return self.__class__._construct_key(self.entity_type, self.entity_id)

    @property
    def id(self) -> Optional[int]:
        return self.entity_id

    @classmethod
    def db(cls) -> Database:
        return Database(cls._db_storage, cls._db_audit)

    @classmethod
    def _construct_key(cls, entity_type: str, entity_id: int) -> str:
        """Construct the database key from type and ID"""
        return f"{entity_type}{cls._SEPARATOR}{entity_id}"

    @classmethod
    def _deconstruct_key(cls, key: str) -> Tuple[str, str]:
        """Deconstruct the database key into type and ID"""
        entity_type, entity_id = key.split(cls._SEPARATOR)
        return (entity_type, entity_id)

    def save(self) -> None:
        """Assign an ID and save the entity to the database"""
        if self.entity_type not in Entity._id_counters:
            Entity._id_counters[self.entity_type] = 0

        attributes = vars(self).copy()
        if attributes.get("db"):
            del attributes["db"]
        del attributes["entity_type"]
        del attributes["entity_id"]
        del attributes["relations"]

        entity_id = self.entity_id
        if entity_id is None:
            entity_id = (
                attributes.get(self._ID_PARAM_NAME)
                or Entity._id_counters[self.entity_type]
            )

        key = self.__class__._construct_key(self.entity_type, entity_id)
        existing_entity = self.__class__.db().load(key)
        if self.entity_id is None and existing_entity:
            raise Exception(f"Entity with key `{key}` already exists in the database")

        self.entity_id = entity_id
        Entity._id_counters[self.entity_type] += 1

        self.db().save(
            self.__class__._construct_key(self.entity_type, self.entity_id),
            [attributes, self.relations],
        )

    def update(self, field: str, value: Any) -> None:
        """Update a specific field of the entity"""
        setattr(self, field, value)
        self.save()

    def get_relations(self, cls: type, relation_name: str) -> List[Any]:
        """Get all related entities of a specific type and relation name"""
        ret = []
        for relation_key in self.relations.get(relation_name, {}):
            (_entity_type, entity_id) = cls._deconstruct_key(relation_key)
            ret.append(cls[entity_id])
        return ret

    def add_relation(
        self, relation_name: str, inverse_relation_name: str, related_entity: "Entity"
    ) -> None:
        """Add a bidirectional relation between this entity and another"""
        if relation_name not in self.relations:
            self.relations[relation_name] = []
        if related_entity.key() in self.relations[relation_name]:
            raise Exception(
                f"In entity {self.key()}, entity with key `{related_entity.key()}` is already in relation `{relation_name}`"
            )
        self.relations[relation_name].append(related_entity.key())

        if inverse_relation_name not in related_entity.relations:
            related_entity.relations[inverse_relation_name] = []
        if self.key() in related_entity.relations[inverse_relation_name]:
            raise Exception(
                f"Entity with key `{self.key()}` is already in relation `{inverse_relation_name}`"
            )
        related_entity.relations[inverse_relation_name].append(self.key())

        self.save()
        related_entity.save()

    def remove_relation(
        self, relation_name: str, inverse_relation_name: str, related_entity: "Entity"
    ) -> None:
        """Remove a bidirectional relation between this entity and another"""
        if relation_name not in self.relations:
            raise Exception(f"Relation {relation_name} not found")
        if related_entity.key() not in self.relations[relation_name]:
            raise Exception(
                f"Entity {related_entity.key()} not found in relation {relation_name}"
            )

        self.relations[relation_name].remove(related_entity.key())

        if inverse_relation_name not in related_entity.relations:
            raise Exception(f"Inverse relation {inverse_relation_name} not found")
        if self.key() not in related_entity.relations[inverse_relation_name]:
            raise Exception(
                f"Entity {self.key()} not found in inverse relation {inverse_relation_name}"
            )
        related_entity.relations[inverse_relation_name].remove(self.key())

        self.save()
        related_entity.save()

    def delete(self) -> None:
        """Delete this entity from the database"""
        if self.entity_id is not None:
            self.db().delete(self.key())
