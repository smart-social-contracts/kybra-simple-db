"""Tests for entity functionality in Kybra Simple DB."""

import pytest

from kybra_simple_db import *


class Person(Entity):
    name = String(min_length=2, max_length=50)
    age = Integer()


class Department(Entity):
    name = String(min_length=2, max_length=50)


@pytest.fixture(autouse=True)
def reset_entity():
    """Reset Entity class variables before each test."""
    Entity._context = set()
    Database._instance = Database(MemoryStorage())
    yield


def test_entity_creation_and_save():
    """Test creating and saving an entity."""
    person = Person(name="John", age=30)
    loaded = Person[person._id]
    assert loaded is not None
    assert loaded.name == "John"
    assert loaded.age == 30


def test_entity_update():
    """Test updating an entity."""
    person = Person(name="John", age=30)
    person.age = 31

    loaded = Person[person._id]
    assert loaded.age == 31


def test_entity_relations():
    """Test entity relations."""
    person = Person(name="John")
    dept = Department(name="IT")

    # Test adding relation
    person.add_relation("works_in", "has_employee", dept)

    # Check person's relations
    loaded_person = Person[person._id]
    loaded_dept = Department[dept._id]

    assert loaded_person.get_relations("works_in", "Department")[0] == dept
    assert loaded_dept.get_relations("has_employee", "Person")[0] == person


def test_entity_duplicate_key():
    """Test that saving an entity with a duplicate ID raises an error."""
    # Create and save first entity
    Person(_id="test_id", name="John", age=30)

    # Try to create and save second entity with same ID
    with pytest.raises(ValueError, match="Entity Person@test_id already exists"):
        Person(_id="test_id", name="Jane", age=25)


def test_getitem_by_id():
    """Test loading an entity by ID using class[id] syntax."""
    # Create and save an entity
    person = Person(_id="John", age=30)

    # Load using class[id] syntax
    loaded_person = Person[person._id]
    assert loaded_person is not None
    assert loaded_person._id == "John"
    assert loaded_person.age == 30

    # Test with non-existent ID
    assert Person["non_existent"] is None


def test_entity_duplicate_relation():
    """Test handling of duplicate relations."""
    person = Person(name="John")
    dept = Department(name="IT")

    # Adding same relation twice should only create one
    person.add_relation("works_in", "has_employee", dept)
    person.add_relation("works_in", "has_employee", dept)

    loaded = Person[person._id]
    assert len(loaded.get_relations("works_in", "Department")) == 1


def test_instances_basic():
    """Test basic functionality of instances() method."""
    # Create multiple persons
    person1 = Person(name="John", age=30)
    person2 = Person(name="Jane", age=25)

    # Retrieve all Person instances by explicitly calling instances()
    persons = Person.instances()

    # Check that we have the correct number of instances
    assert len(persons) == 2

    # Check that the instances match the saved persons
    saved_ids = {person1._id, person2._id}
    retrieved_ids = {p._id for p in persons}
    assert saved_ids == retrieved_ids


def test_instances_with_type_name():
    """Test instances() method with explicit type name."""
    # Create a Person and a Department
    Person(name="John", age=30)
    Department(name="Engineering")

    # Retrieve Person instances using explicit type name by calling instances()
    persons = Person.instances()
    departments = Department.instances()

    # Check that we have the correct number of instances for each type
    assert len(persons) == 1
    assert len(departments) == 1

    # Check that the instances are of the correct type
    assert all(isinstance(p, Person) for p in persons)
    assert all(isinstance(d, Department) for d in departments)


def test_instances_empty():
    """Test instances() method when no instances exist."""

    # Create a new entity type
    class NewEntity(Entity):
        pass

    # Retrieve instances by calling instances()
    instances = NewEntity.instances()

    # Check that no instances are returned
    assert len(instances) == 0


def test_instances_with_multiple_types():
    """Test instances() method with multiple entity types."""
    # Create multiple entities of different types
    Person(name="John", age=30)
    Person(name="Jane", age=25)
    Department(name="Engineering")

    # Retrieve instances for each type by calling instances()
    persons = Person.instances()
    departments = Department.instances()

    # Check the number of instances for each type
    assert len(persons) == 2
    assert len(departments) == 1


def test_entity_inheritance():
    """Test entity inheritance and type-based instance querying."""

    # Define test classes
    class Animal(Entity, TimestampedMixin):
        pass

    class Dog(Animal):
        pass

    class Cat(Animal):
        pass

    # Create test instances
    animal_a = Animal(name="Alice")
    dog_b = Dog(name="Bob")
    cat_c = Cat(name="Charlie")

    # Test instance querying
    all_animals = Animal.instances()
    assert len(all_animals) == 3
    assert any(a.name == "Alice" for a in all_animals)
    assert any(a.name == "Bob" for a in all_animals)
    assert any(a.name == "Charlie" for a in all_animals)

    dogs = Dog.instances()
    assert len(dogs) == 1
    assert dogs[0].name == "Bob"

    cats = Cat.instances()
    assert len(cats) == 1
    assert cats[0].name == "Charlie"

    # Clean up
    animal_a.delete()
    dog_b.delete()
    cat_c.delete()
