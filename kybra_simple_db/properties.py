"""Property definitions for Entity classes."""

from dataclasses import dataclass
from typing import Any, Callable, Optional, Type

from .entity import Entity

# Prefix used for storing property values in entity __dict__
PROPERTY_STORAGE_PREFIX = "prop"


@dataclass
class Property:
    """Definition of an entity property.

    Attributes:
        name: Name of the property
        type: Type of the property (e.g. str, int)
        default: Default value if not set
        validator: Optional function to validate values
    """

    name: str
    type: Type
    default: Any = None
    validator: Optional[Callable[[Any], bool]] = None

    def __set_name__(self, owner, name):
        """Set the property name when class is created."""
        self.name = name

    def __get__(self, obj, objtype=None):
        """Get the property value."""
        if obj is None:
            return self
        return obj.__dict__.get(f"_{PROPERTY_STORAGE_PREFIX}_{self.name}", self.default)

    def __set__(self, obj, value):
        """Set the property value with type checking and validation."""
        if value is not None:
            if not isinstance(value, self.type):
                if isinstance(value, str) and self.type in (int, float, bool):
                    try:
                        if self.type == bool:
                            value = value.lower() in ("true", "1", "yes", "on")
                        else:
                            value = self.type(value)
                    except (ValueError, TypeError):
                        raise TypeError(
                            f"{self.name} must be of type {self.type.__name__}"
                        )
                else:
                    raise TypeError(f"{self.name} must be of type {self.type.__name__}")

            if self.validator and not self.validator(value):
                raise ValueError(f"Invalid value for {self.name}: {value}")

        obj.__dict__[f"_{PROPERTY_STORAGE_PREFIX}_{self.name}"] = value
        obj._save()


class String(Property):
    """String property with optional length validation."""

    def __init__(
        self,
        min_length: int = None,
        max_length: int = None,
        default: str = None,
    ):
        def validator(value: str) -> bool:
            if min_length is not None and len(value) < min_length:
                return False
            if max_length is not None and len(value) > max_length:
                return False
            return True

        super().__init__(name="", type=str, default=default, validator=validator)


class Integer(Property):
    """Integer property with optional range validation."""

    def __init__(
        self, min_value: int = None, max_value: int = None, default: int = None
    ):
        def validator(value: int) -> bool:
            if min_value is not None and value < min_value:
                return False
            if max_value is not None and value > max_value:
                return False
            return True

        super().__init__(name="", type=int, default=default, validator=validator)


class Float(Property):
    """Float property with optional range validation."""

    def __init__(
        self, min_value: float = None, max_value: float = None, default: float = None
    ):
        def validator(value: float) -> bool:
            if min_value is not None and value < min_value:
                return False
            if max_value is not None and value > max_value:
                return False
            return True

        super().__init__(name="", type=float, default=default, validator=validator)


class Boolean(Property):
    """Boolean property."""

    def __init__(self, default: bool = None):
        super().__init__(name="", type=bool, default=default)


class Relation:
    """Base property for defining and accessing relations.

    This is the base class for all relation properties. It provides common functionality
    for managing relationships between entities.

    For one-to-one relationships (default), this property returns a single entity and
    enforces single cardinality. For one-to-many or many-to-many relationships, it
    returns a list of entities.
    """

    def __init__(
        self,
        entity_types: [str],
        reverse_name: str = None,
        many: bool = False,
    ):
        """Initialize relation property.

        Args:
            entity_types: Type names of related entities
            reverse_name: Optional name for reverse relation
            many: Whether this property can hold multiple entities (default: False)
        """
        self.entity_types = entity_types
        self.name = None
        self.reverse_name = reverse_name
        self.many = many

    def __set_name__(self, owner, name):
        """Set the property name when class is created."""
        self.name = name
        if self.reverse_name is None:
            self.reverse_name = name

    def __get__(self, obj, objtype=None):
        """Get related entities."""
        if obj is None:
            return self
        relations = obj.get_relations(self.name)
        if not self.many:
            # For single relationships, return the first entity or None
            return relations[0] if relations else None
        return relations

    def __set__(self, obj, value):
        """Set related entities.

        Args:
            value: For many=False: a single Entity instance
                  For many=True: a list/tuple of Entity instances
        """
        if self.many:
            if not isinstance(value, (list, tuple)):
                raise TypeError(f"{self.name} requires a list or tuple of entities")
            values_list = value
        else:
            values_list = [value]

        # Get existing and new relations as sets
        existing = set(obj.get_relations(self.name))
        new = set(values_list)

        # For one-to-many, check if entities have existing relations
        if isinstance(self, OneToMany):
            for entity in new:
                existing_relations = entity.get_relations(self.reverse_name)
                if existing_relations:
                    old_relation = existing_relations[0]
                    if old_relation != obj:
                        # Remove the entity from the old relation's list
                        old_relation._relations[self.name].remove(entity)
                        # Remove the old relation from the entity's list
                        entity._relations[self.reverse_name].remove(old_relation)

        # Remove relations that are not in new set
        to_remove = existing - new
        for entity in to_remove:
            obj.remove_relation(self.name, self.reverse_name, entity)

        # Add relations that are not in existing set
        to_add = new - existing
        for entity in to_add:
            obj.add_relation(self.name, self.reverse_name, entity)

    def validate_entity(self, entity):
        """Validate that an entity is of the correct type.

        Handles both namespaced (e.g., "app::User") and non-namespaced (e.g., "User") types.
        """
        if entity is None:
            return True
        if not isinstance(entity, Entity):
            raise TypeError(f"{self.name} must be set to Entity instances")

        # Convert entity_types to list for uniform handling
        allowed_types = (
            [self.entity_types]
            if isinstance(self.entity_types, str)
            else self.entity_types
        )

        # Check if entity type matches any allowed type
        # This handles both exact matches and namespace variations
        if entity._type not in allowed_types:
            # Also check if the class name matches (for backward compatibility)
            entity_class_name = (
                entity._type.split("::")[-1] if "::" in entity._type else entity._type
            )
            type_matches = any(
                entity_class_name == (t.split("::")[-1] if "::" in t else t)
                for t in allowed_types
            )
            if not type_matches:
                raise TypeError(
                    f"{self.name} must be set an Entity instance of any of the following types: {self.entity_types}, "
                    f"but got type '{entity._type}'"
                )

    def resolve_entity(self, obj, value):
        """Resolve a value to an Entity instance.

        Args:
            obj: The entity object that owns this relation
            value: Can be an Entity instance, string ID, or string name/alias

        Returns:
            Entity instance or None
        """
        if value is None:
            return None

        if isinstance(value, Entity):
            return value

        if isinstance(value, (str, int)):
            # Try to find entity by ID or name (alias) using each allowed entity type
            entity_types = (
                [self.entity_types]
                if isinstance(self.entity_types, str)
                else self.entity_types
            )
            for entity_type_name in entity_types:
                # Get the entity class from the database registry
                # Try full type name first (with namespace)
                entity_class = obj.db()._entity_types.get(entity_type_name)

                # If not found and type name has namespace separator, try without namespace as fallback
                if not entity_class and "::" not in entity_type_name:
                    # Type name has no namespace, try to find any class with this name
                    # This is for backward compatibility
                    entity_class = obj.db()._entity_types.get(entity_type_name)

                if entity_class:
                    found_entity = entity_class[value]
                    if found_entity:
                        return found_entity

            raise ValueError(
                f"No entity of types {self.entity_types} found with ID or name '{value}'"
            )

        raise TypeError(
            f"{self.name} must be set to an Entity instance, string ID, or string name"
        )


class RelationList:
    """Helper class for managing lists of related entities."""

    def __init__(self, obj, prop):
        self.obj = obj
        self.prop = prop

    def add(self, entity):
        """Add a new relation."""
        # Resolve entity (supports string ID/name)
        entity = self.prop.resolve_entity(self.obj, entity)

        # Validate entity type using the base validate_entity method
        self.prop.validate_entity(entity)

        # For one-to-many, check if entity already has a relation
        if isinstance(self.prop, OneToMany):
            existing_relations = entity.get_relations(self.prop.reverse_name)
            if existing_relations:
                # Remove existing relation since it's one-to-many
                old_relation = existing_relations[0]
                # Remove the entity from the old relation's list
                if old_relation != self.obj:
                    old_relation._relations[self.prop.name].remove(entity)
                    # Remove the old relation from the entity's list
                    entity._relations[self.prop.reverse_name].remove(old_relation)

        self.obj.add_relation(self.prop.name, self.prop.reverse_name, entity)

    def remove(self, entity):
        """Remove a relation."""
        self.obj.remove_relation(self.prop.name, self.prop.reverse_name, entity)

    def __iter__(self):
        return iter(self.obj.get_relations(self.prop.name))

    def __len__(self):
        return len(self.obj.get_relations(self.prop.name))


class OneToOne(Relation):
    """Property for defining one-to-one relationships.

    This property type represents a one-to-one relationship where each entity
    can be related to exactly one entity on the other side.

    Example:
        class Person(Entity):
            profile = OneToOne('Profile', 'person')

        class Profile(Entity):
            person = OneToOne('Person', 'profile')
    """

    def __init__(self, entity_types: [str], reverse_name: str = None):
        super().__init__(entity_types, reverse_name, many=False)

    def __set__(self, obj, value):
        """Set the related entity with one-to-one constraints."""
        if value is not None:
            # Check if trying to set multiple values
            if isinstance(value, (list, tuple)):
                raise ValueError(
                    f"{self.name} cannot be set to multiple values (one-to-one relationship)"
                )

            # Validate entity type
            value = self.resolve_entity(obj, value)

            # Check that the reverse property is OneToOne
            reverse_prop = value.__class__.__dict__.get(self.reverse_name)
            if not isinstance(reverse_prop, OneToOne):
                raise ValueError(
                    f"Reverse property '{self.reverse_name}' must be OneToOne"
                )

            # Get current value if any
            current = self.__get__(obj)
            if current is not None:
                # Remove existing relation
                obj.remove_relation(self.name, self.reverse_name, current)

            # Check if value is already related to another entity and remove that relation
            existing = value.get_relations(self.reverse_name)
            if existing:
                existing_entity = existing[0]
                # Remove the existing relation from both sides
                existing_entity.remove_relation(self.name, self.reverse_name, value)
                value.remove_relation(self.reverse_name, self.name, existing_entity)

        # Set the new relation
        super().__set__(obj, value)


class OneToMany(Relation):
    """Property for defining one-to-many relationships.

    This property type represents a one-to-many relationship where the 'one' side
    owns multiple instances of the 'many' side, but each 'many' instance belongs to
    only one owner.

    Example:
        class Department(Entity):
            employees = OneToMany('Employee', 'department')

        class Employee(Entity):
            department = ManyToOneProperty('Department', 'employees')
    """

    def __init__(self, entity_types: [str], reverse_name: str):
        super().__init__(entity_types, reverse_name, many=True)

    def __set__(self, obj, values):
        """Set related entities with one-to-many constraints."""
        if not isinstance(values, (list, tuple)):
            raise TypeError(f"{self.name} must be set to a list of entities")

        resolved_values = []
        for value in values:
            # Resolve value to Entity instance
            resolved_value = self.resolve_entity(obj, value)

            # Validate entity type using the base validate_entity method
            self.validate_entity(resolved_value)
            resolved_values.append(resolved_value)

            # Check that the reverse property is ManyToOne
            reverse_prop = resolved_value.__class__.__dict__.get(self.reverse_name)
            if not isinstance(reverse_prop, ManyToOne):
                raise ValueError(
                    f"Reverse property '{self.reverse_name}' must be ManyToOne"
                )

        # Replace original values with resolved entities
        super().__set__(obj, resolved_values)

    def __get__(self, obj, objtype=None):
        """Get related entities as a RelationList."""
        if obj is None:
            return self
        return RelationList(obj, self)


class ManyToOne(Relation):
    """Property for defining many-to-one relationships.

    This property type represents a many-to-one relationship where multiple entities
    can belong to a single owner entity.

    Example:
        class Employee(Entity):
            department = ManyToOneProperty('Department', 'employees')

        class Department(Entity):
            employees = OneToMany('Employee', 'department')
    """

    def __init__(self, entity_types: [str], reverse_name: str = None):
        super().__init__(entity_types, reverse_name, many=False)

    def __set__(self, obj, value):
        """Set the related entity with many-to-one constraints."""
        if value is not None:
            # Check if trying to set multiple values
            if isinstance(value, (list, tuple)):
                raise ValueError(
                    f"{self.name} cannot be set to multiple values (many-to-one relationship)"
                )

            # Resolve value to Entity instance
            value = self.resolve_entity(obj, value)

            # Validate entity type using the base validate_entity method
            self.validate_entity(value)

            # Check that the reverse property is OneToMany
            reverse_prop = value.__class__.__dict__.get(self.reverse_name)
            if not reverse_prop:
                raise ValueError(
                    f"Reverse property '{self.reverse_name}' not found in {value.__class__.__name__} entity"
                )

            if not isinstance(reverse_prop, OneToMany):
                raise ValueError(
                    f"Reverse property '{self.reverse_name}' must be OneToMany and it is '{reverse_prop.__class__.__name__}'"
                )

        super().__set__(obj, value)


class ManyToMany(Relation):
    """Property for defining many-to-many relationships.

    This property type represents a many-to-many relationship where entities
    on both sides can be related to multiple entities on the other side.

    Example:
        class Student(Entity):
            courses = ManyToManyProperty('Course', 'students')

        class Course(Entity):
            students = ManyToManyProperty('Student', 'courses')
    """

    def __init__(self, entity_types: [str], reverse_name: str):
        super().__init__(entity_types, reverse_name, many=True)

    def __set__(self, obj, values):
        """Set related entities with many-to-many constraints."""
        # Convert single entity to list for convenience
        if isinstance(values, Entity):
            values = [values]
        elif isinstance(values, (str, int)):
            # Handle single string ID/name
            values = [values]
        elif values is not None and not isinstance(values, (list, tuple)):
            raise TypeError(f"{self.name} must be set to an entity or list of entities")

        if values is not None:
            resolved_values = []
            for value in values:
                # Resolve value to Entity instance
                resolved_value = self.resolve_entity(obj, value)

                # Validate entity type using the base validate_entity method
                self.validate_entity(resolved_value)
                resolved_values.append(resolved_value)

                # Check that the reverse property is ManyToMany
                reverse_prop = resolved_value.__class__.__dict__.get(self.reverse_name)
                if not isinstance(reverse_prop, ManyToMany):
                    raise ValueError(
                        f"Reverse property '{self.reverse_name}' must be ManyToMany"
                    )

            # Replace original values with resolved entities
            values = resolved_values

        super().__set__(obj, values)

    def __get__(self, obj, objtype=None):
        """Get related entities as a RelationList."""
        if obj is None:
            return self
        return RelationList(obj, self)
