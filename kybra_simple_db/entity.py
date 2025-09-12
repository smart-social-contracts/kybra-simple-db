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

    This is the core class for all database entities. It provides automatic ID generation,
    property storage, relationship management, and alias-based lookups.

    Usage Examples:
        # Basic entity with auto-generated ID
        class User(Entity):
            name = String(min_length=2, max_length=50)
            age = Integer(min_value=0)

        user = User(name="John", age=30)  # Creates entity with _id="1"

        # Entity with alias for lookups
        class Person(Entity):
            __alias__ = "name"  # Enables Person["John"] lookup
            name = String()

        person = Person(name="Jane")
        found = Person["Jane"]  # Lookup by alias

    Key Features:
        - Auto-generated sequential IDs (_id: "1", "2", "3", ...)
        - Property validation and type checking via descriptors
        - Relationship management (OneToOne, OneToMany, ManyToMany)
        - Alias-based entity lookup (Entity["alias_value"])
        - Automatic persistence to database on creation/update
        - Entity counting and pagination support

    Internally managed attributes:
        _type (str): Entity class name (e.g., "User", "Person")
        _id (str): Unique sequential identifier ("1", "2", "3", ...)
        _loaded (bool): True if loaded from DB, False if newly created
        _counted (bool): True if entity has been counted (prevents double-counting)
        _relations (dict): Dictionary mapping relation names to related entities
        _do_not_save (bool): Temporary flag to prevent saving during initialization

    Class-level attributes:
        __alias__ (str): Optional field name for alias-based lookups
        _entity_type (str): Optional entity type for subclasses
        _context (Set[Entity]): Set of all entities in current context

    Property Storage:
        User-defined properties (String, Integer, etc.) are stored as _prop_{name}
        in the entity's __dict__ to avoid conflicts with internal attributes.
        Example: name = String() stores value in _prop_name
    """

    _entity_type = None  # To be defined in subclasses
    _context: Set["Entity"] = set()  # Set of entities in current context
    _do_not_save = False

    def __init__(self, **kwargs):
        """Initialize a new entity.

        Creates a new entity instance with auto-generated ID and sets up all internal
        attributes. User-provided properties are validated and stored using the
        _prop_{name} pattern to avoid conflicts with internal attributes.

        The entity is automatically:
        - Assigned a sequential ID (_id)
        - Registered with the database
        - Added to the class context
        - Persisted to storage via _save()

        Args:
            **kwargs: User-defined attributes to set on the entity.
                     These correspond to properties defined on the class
                     (e.g., name="John" for a String() property named 'name').

                     Special internal kwargs (used internally by the system):
                     - _id: Custom ID string (bypasses auto-generation)

        Example:
            class User(Entity):
                name = String(min_length=2)
                age = Integer(min_value=0)

            # Creates new entity with _id="1", validates and stores properties
            user = User(name="Alice", age=25)
        """
        # Initialize any mixins
        super().__init__() if hasattr(super(), "__init__") else None

        # Store the type for this entity - always use class name
        self._type = self.__class__.__name__
        # Get next sequential ID from storage
        self._id = None if kwargs.get("_id") is None else kwargs["_id"]
        self._loaded = False if kwargs.get("_loaded") is None else kwargs["_loaded"]
        self._counted = False  # Track if this entity has been counted

        self._relations = {}

        # Add to context
        self.__class__._context.add(self)

        # Register this type with the database
        self.db().register_entity_type(self.__class__)

        # Generate ID if not provided
        if self._id is None:
            db = self.db()
            type_name = self._type
            current_id = db.load("_system", f"{type_name}_id")
            if current_id is None:
                current_id = "0"
            next_id = str(int(current_id) + 1)
            self._id = next_id
            db.save("_system", f"{type_name}_id", self._id)

        # Register this instance in the entity registry
        self.db().register_entity(self)

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

        type_name = self.__class__.__name__
        db = self.__class__.db()

        if self._id is None:
            # Increment the ID when a new entity is created (never reuse or decrement)
            self._id = str(int(db.load("_system", f"{type_name}_id") or 0) + 1)
            db.save("_system", f"{type_name}_id", self._id)
            # Increment the count when a new entity is created and decrement when deleted
            if not self._counted:
                count_key = f"{type_name}_count"
                current_count = int(db.load("_system", count_key) or 0)
                db.save("_system", count_key, str(current_count + 1))
                self._counted = True
        else:
            if not self._loaded:
                if db.load(type_name, self._id) is not None:
                    raise ValueError(f"Entity {self._type}@{self._id} already exists")
                else:
                    # Increment count for new entities with custom IDs
                    if not self._counted:
                        count_key = f"{type_name}_count"
                        current_count = int(db.load("_system", count_key) or 0)
                        db.save("_system", count_key, str(current_count + 1))
                        self._counted = True

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
        data = self.serialize()

        if not self._do_not_save:
            logger.debug(f"Saving entity {self._type}@{self._id} to database")
            db = self.db()
            db.save(self._type, self._id, data)
            if hasattr(self.__class__, "__alias__") and self.__class__.__alias__:
                alias_field = self.__class__.__alias__
                if hasattr(self, alias_field):
                    alias_value = getattr(self, alias_field)
                    if alias_value is not None:
                        db.save(self._type + "_alias", alias_value, self._id)
            self._loaded = True

        return self

    @classmethod
    def _alias_key(cls: Type[T]) -> str:
        return cls.__name__ + "_alias"

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
        logger.debug(f"Loading entity {entity_id} (level={level})")
        if level == 0:
            return None

        if not entity_id:
            return None

        # Use class name for type
        type_name = cls.__name__

        # Check entity registry first
        db = cls.db()
        existing_entity = db.get_entity(type_name, entity_id)
        if existing_entity is not None:
            logger.debug(f"Found entity {type_name}@{entity_id} in registry")
            return existing_entity

        logger.debug(f"Loading entity {type_name}@{entity_id} from database")
        data = db.load(type_name, entity_id)
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
        L = [_.serialize() for _ in cls.instances()]
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
        db.register_entity_type(cls)
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

    @classmethod
    def count(cls: Type[T]) -> int:
        """Get the total count of entities of this type.

        Returns:
            int: Total number of entities
        """
        type_name = cls.__name__
        db = cls.db()
        count_key = f"{type_name}_count"
        count = db.load("_system", count_key)
        return int(count) if count else 0

    @classmethod
    def max_id(cls: Type[T]) -> int:
        """Get the maximum ID assigned to entities of this type.

        Returns:
            int: Maximum entity ID
        """
        type_name = cls.__name__
        db = cls.db()
        max_id_key = f"{type_name}_id"
        max_id = db.load("_system", max_id_key)
        return int(max_id) if max_id else 0

    @classmethod
    def load_some(
        cls: Type[T],
        from_id: int,
        count: int = 10,
    ) -> List[T]:
        """Load some entities.

        Args:
            from_id (int): ID of the first entity to load
            count (int): Number of entities to load

        Returns:
            List[T]: List of entities for the requested page

        Raises:
            ValueError: If page or page_size is less than 1
        """
        if from_id < 1:
            raise ValueError("from_id must be at least 1")
        if count < 1:
            raise ValueError("count must be at least 1")

        # Return the slice of entities for the requested page
        ret = []
        while len(ret) < count and from_id <= cls.max_id():
            entity = cls.load(str(from_id))
            if entity:
                ret.append(entity)
            from_id += 1

        return ret

    def delete(self) -> None:
        logger.debug(f"Deleting entity {self._type}@{self._id}")
        """Delete this entity from the database."""
        self.db().delete(self._type, self._id)

        # Remove from entity registry
        self.db().unregister_entity(self._type, self._id)

        # Decrement the count when an entity is deleted
        type_name = self.__class__.__name__
        count_key = f"{type_name}_count"
        current_count = int(self.db().load("_system", count_key) or 0)
        if current_count > 0:
            self.db().save("_system", count_key, str(current_count - 1))
        else:
            raise ValueError(
                f"Entity count for {type_name} is already zero; cannot decrement further."
            )

        # Remove from alias mappings when deleted
        if hasattr(self.__class__, "__alias__") and self.__class__.__alias__:
            alias_field = self.__class__.__alias__
            if hasattr(self, alias_field):
                alias_value = getattr(self, alias_field)
                if alias_value is not None:
                    self.db().delete(self._alias_key(), alias_value)

        logger.debug(f"Deleted entity {self._type}@{self._id}")

        # Remove from context
        self.__class__._context.discard(self)

    def serialize(self) -> Dict[str, Any]:
        """Convert the entity to a serializable dictionary.

        Returns:
            Dict containing the entity's serializable data
        """
        # Get mixin data first if available
        data = super().serialize() if hasattr(super(), "serialize") else {}

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
        reference_name = "_id"  # TODO: make this configurable, e.g. take alias instead
        for rel_name, rel_entities in self._relations.items():
            if rel_entities:
                # Check if this is a *ToMany relation that should always be a list
                rel_prop = getattr(self.__class__, rel_name, None)
                from kybra_simple_db.properties import OneToMany, ManyToMany
                is_to_many = isinstance(rel_prop, (OneToMany, ManyToMany))
                
                if len(rel_entities) == 1 and not is_to_many:
                    # Single relation for OneToOne/ManyToOne - store as single reference
                    data[rel_name] = getattr(rel_entities[0], reference_name)
                else:
                    # Multiple relations or *ToMany relations - store as list of references
                    data[rel_name] = [getattr(e, reference_name) for e in rel_entities]

        return data

    @classmethod
    def __class_getitem__(cls: Type[T], key: Any) -> Optional[T]:
        """Allow using class[id] syntax to load entities.

        Args:
            key: ID of entity to load or value of aliased field

        Returns:
            Entity if found, None otherwise
        """
        logger.debug(f"Loading entity with key {key}")
        # First try as direct ID lookup (convert to string if numeric)
        str_key = str(key) if isinstance(key, (int, float)) else key
        entity = cls.load(str_key)
        if entity:
            return entity

        logger.debug(f"Entity not found by ID {str_key}")

        # If entity not found by ID and class has __alias__ defined, try by alias
        if hasattr(cls, "__alias__") and cls.__alias__:
            alias_key = cls._alias_key()
            logger.debug(
                f"Trying to find entity by alias key {alias_key} with value {str_key}"
            )
            actual_key = cls.db().load(alias_key, str_key)
            if actual_key:
                logger.debug(
                    f"Found entity by alias key {alias_key} with value {str_key}"
                )
                return cls.load(actual_key)
            else:
                logger.debug(
                    f"Entity not found by alias key {alias_key} with value {str_key}"
                )

        return None

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
