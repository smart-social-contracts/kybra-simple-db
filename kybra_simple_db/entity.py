"""Enhanced entity implementation with support for mixins and entity types."""

import os
from typing import Any, Dict, List, Optional, Set, Type, TypeVar

from kybra_simple_logging import get_logger

from .constants import LEVEL_MAX_DEFAULT
from .db_engine import Database

logger = get_logger(__name__)


T = TypeVar("T", bound="Entity")


class Entity:
    """Base class for database entities with enhanced features.

    Attributes:
        _type (str): Type of the entity
        _id (str): Unique identifier for the entity
        _relations (dict): Dictionary of related entities
        _entity_type (str): Entity type for subclasses (optional)
    """

    _entity_type = None  # To be defined in subclasses
    _context: Set["Entity"] = set()  # Set of entities in current context
    _do_not_save = False

    def __init__(self, **kwargs):
        """Initialize a new entity.

        Args:
            type_name: Type name for the entity. If not provided, uses class name
            id: Optional ID for the entity. If not provided, one will be generated.
            **kwargs: Additional attributes to set on the entity
        """
        # Initialize any mixins
        super().__init__() if hasattr(super(), "__init__") else None

        # Store the type for this entity - always use class name
        self._type = self.__class__.__name__
        # Get next sequential ID from storage
        self._id = None if kwargs.get("_id") is None else kwargs["_id"]
        self._loaded = False if kwargs.get("_loaded") is None else kwargs["_loaded"]

        self._relations = {}

        # Add to context
        self.__class__._context.add(self)

        # Register this type with the database
        self.db().register_entity_type(self.__class__)

        self._do_not_save = True
        # Set additional attributes
        for k, v in kwargs.items():
            if not k.startswith("_"):
                setattr(self, k, v)
        self._do_not_save = False

        self._save()

    @classmethod
    def new(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    def db(cls) -> Database:
        """Get the database instance.

        Returns:
            Database: The database instance
        """
        return Database.get_instance()

    def _save(
        self,
    ) -> "Entity":
        """Save the entity to the database.

        Returns:
            Entity: self for chaining

        Raises:
            PermissionError: If TimestampedMixin is used and caller is not the owner
        """

        if self._id is None:
            self._id = str(self.db().get_next_id())
        elif not self._loaded:
            type_name = self.__class__.__name__
            db = self.__class__.db()
            if db.load(type_name, self._id) is not None:
                raise ValueError(f"Entity {self._type}@{self._id} already exists")

        logger.debug(f"Saving entity {self._type}@{self._id}")

        # Update timestamps if mixin is present
        if hasattr(self, "_update_timestamps"):
            caller_id = os.environ.get("CALLER_ID", "system")
            if (
                hasattr(self, "check_ownership")
                and hasattr(self, "_timestamp_created")
                and self._timestamp_created
            ):
                if not self.check_ownership(caller_id):
                    raise PermissionError(
                        f"Only the owner can update this entity. Current owner: {self._owner}"
                    )
            self._update_timestamps(caller_id)

        # Save to database
        data = self.to_dict()

        if not self._do_not_save:
            logger.debug(f"Data to save: {data}")
            db = self.db()
            logger.debug(f"Database instance: {db}")
            db.save(self._type, self._id, data)
            self._loaded = True

            # print('traceback', '\n'.join(traceback.format_stack()))

        return self

    @classmethod
    def load(
        cls: Type[T], entity_id: str = None, level: int = LEVEL_MAX_DEFAULT
    ) -> Optional[T]:
        """Load an entity from the database.

        Args:
            id: ID of entity to load

        Returns:
            Entity if found, None otherwise
        """
        logger.debug(f"Loading entity {entity_id} with level {level}")
        if level == 0:
            return None

        if not entity_id:
            return None

        # Use class name for type
        type_name = cls.__name__
        logger.debug(f"Loading entity {type_name}@{entity_id}")

        db = cls.db()
        logger.debug(f"Database instance: {db}")
        data = db.load(type_name, entity_id)
        logger.debug(f"Loaded data: {data}")
        if not data:
            return None

        # Create instance first
        entity = cls(**data, _loaded=True)

        # Extract relations
        relations = {}
        if "relations" in data:
            relations_data = data.pop("relations")
            for rel_name, rel_refs in relations_data.items():
                relations[rel_name] = []
                for ref in rel_refs:
                    related = (
                        Entity.db()
                        ._entity_types[ref["_type"]]
                        .load(ref["_id"], level=level - 1)
                    )
                    if related:
                        relations[rel_name].append(related)

        # Set relations after loading
        entity._relations = relations

        return entity

    @classmethod
    def find(cls: Type[T], d) -> List[T]:
        D = d
        L = [_.to_dict() for _ in cls.instances()]
        return [
            cls.load(d["_id"]) for d in L if all(d.get(k) == v for k, v in D.items())
        ]

    @classmethod
    def instances(cls: Type[T]) -> List[T]:
        """Get all instances of this entity type, including subclass instances.

        Returns:
            List of entities
        """
        db = Database.get_instance()
        instances = []

        # Get all keys from storage
        for key in db._db_storage.keys():
            parts = key.split("@")
            if len(parts) != 2:
                continue

            stored_type, entity_id = parts

            # Load the data to check its type
            data = db.load(stored_type, entity_id)
            if not data:
                continue

            # Create instance if it's a subclass of the requested type
            # or if it's the exact same type
            if stored_type == cls.__name__ or db.is_subclass(stored_type, cls):
                # Use the actual stored type's load method
                actual_cls = db._entity_types.get(stored_type)
                if actual_cls:
                    instance = actual_cls.load(entity_id)
                    if instance:
                        instances.append(instance)

        return instances

    def delete(self) -> None:
        logger.debug(f"Deleting entity {self._type}@{self._id}")
        """Delete this entity from the database."""
        self.db().delete(self._type, self._id)

        logger.debug(f"Deleted entity {self._type}@{self._id}")

        # Remove from context
        self.__class__._context.discard(self)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the entity to a dictionary.

        Returns:
            Dict containing the entity's data
        """
        # Get mixin data first if available
        data = super().to_dict() if hasattr(super(), "to_dict") else {}

        # Add core entity data
        data.update(
            {
                "_type": self._type,  # Use the entity type
                "_id": self._id,
            }
        )

        # Add all property descriptors from class hierarchy
        from kybra_simple_db.properties import Property

        for cls in reversed(self.__class__.__mro__):
            for k, v in cls.__dict__.items():
                if not k.startswith("_") and isinstance(v, Property):
                    data[k] = getattr(self, k)

        # Add instance attributes
        for k, v in self.__dict__.items():
            if not k.startswith("_"):
                data[k] = v

        # Add relations as references
        relations = {}
        for rel_name, rel_entities in self._relations.items():
            relations[rel_name] = [
                {"_type": e._type, "_id": e._id} for e in rel_entities
            ]
        if relations:
            data["relations"] = relations

        return data

    @classmethod
    def __class_getitem__(cls: Type[T], entity_id: str) -> Optional[T]:
        """Allow using class[id] syntax to load entities.

        Args:
            id: ID of entity to load

        Returns:
            Entity if found, None otherwise
        """
        return cls.load(entity_id)

    def __eq__(self, other: object) -> bool:
        """Compare entities based on type and ID.

        Args:
            other: Object to compare with

        Returns:
            True if entities are equal, False otherwise
        """
        if not isinstance(other, Entity):
            return NotImplemented
        return self._type == other._type and self._id == other._id

    def __hash__(self) -> int:
        """Hash entity based on type and ID.

        Returns:
            Hash value
        """
        return hash((self._type, self._id))

    def add_relation(self, from_rel: str, to_rel: str, other: "Entity") -> None:
        """Add a bidirectional relationship with another entity.

        Args:
            from_rel: Name of relation from this entity to other
            to_rel: Name of relation from other entity to this
            other: Entity to create relationship with
        """
        # Add forward relation
        if from_rel not in self._relations:
            self._relations[from_rel] = []
        if other not in self._relations[from_rel]:
            self._relations[from_rel].append(other)

        # Add reverse relation
        if to_rel not in other._relations:
            other._relations[to_rel] = []
        if self not in other._relations[to_rel]:
            other._relations[to_rel].append(self)

        # Save both entities
        self._save()
        other._save()

    def get_relations(
        self, relation_name: str, entity_type: str = None
    ) -> List["Entity"]:
        """Get all related entities for a relation, optionally filtered by type.

        Args:
            relation_name: Name of the relation to follow
            entity_type: Optional type name to filter entities by

        Returns:
            List of related entities
        """
        if relation_name not in self._relations:
            return []

        entities = self._relations[relation_name]
        if entity_type:
            entities = [e for e in entities if e._type == entity_type]

        return entities

    def remove_relation(self, from_rel: str, to_rel: str, other: "Entity") -> None:
        """Remove a bidirectional relationship with another entity.

        Args:
            from_rel: Name of relation from this entity to other
            to_rel: Name of relation from other entity to this
            other: Entity to remove relationship with
        """
        # Remove forward relation
        if from_rel in self._relations:
            if other in self._relations[from_rel]:
                self._relations[from_rel].remove(other)

        # Remove reverse relation
        if to_rel in other._relations:
            if self in other._relations[to_rel]:
                other._relations[to_rel].remove(self)

        # Save both entities
        self._save()
        other._save()
