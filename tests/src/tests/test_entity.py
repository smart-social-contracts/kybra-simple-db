"""Tests for entity functionality in Kybra Simple DB."""

from tester import Tester

from kybra_simple_db import *


class Person(Entity):
    """Test entity class."""

    def __init__(self, name: str, age: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.age = age

    name = String(min_length=2, max_length=50)
    age = Integer()
    __alias__ = "name"


class Department(Entity):
    name = String(min_length=2, max_length=50)


class TestEntity:
    def setUp(self):
        """Reset Entity class variables before each test."""
        Database.get_instance().clear()

    def test_entity_creation_and_save(self):
        """Test creating and saving an entity."""
        person = Person(name="John", age=30)
        loaded = Person[person._id]
        assert loaded is not None
        assert loaded.name == "John"
        assert loaded.age == 30

    def test_entity_update(self):
        """Test updating an entity."""
        person = Person(name="John", age=30)
        person.age = 31

        loaded = Person[person._id]
        assert loaded.age == 31

    def test_entity_relations(self):
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

    def test_entity_duplicate_key(self):
        """Test that saving an entity with a duplicate ID raises an error."""
        # Create and save first entity
        Person(_id="test_id", name="John", age=30)

        # Try to create and save second entity with same ID
        try:
            Person(_id="test_id", name="Jane", age=25)
            assert False, "Entity Person@test_id already exists"
        except ValueError as e:
            assert str(e) == "Entity Person@test_id already exists"

    def test_getitem_by_id(self):
        """Test loading an entity by ID using class[id] syntax."""
        # Create and save an entity
        person = Person(_id="John", name="John", age=30)

        # Load using class[id] syntax
        loaded_person = Person[person._id]
        assert loaded_person is not None
        assert loaded_person._id == "John"
        assert loaded_person.age == 30

        # Test with non-existent ID
        assert Person["non_existent"] is None

    def test_entity_duplicate_relation(self):
        """Test handling of duplicate relations."""
        person = Person(name="John")
        dept = Department(name="IT")

        # Adding same relation twice should only create one
        person.add_relation("works_in", "has_employee", dept)
        person.add_relation("works_in", "has_employee", dept)

        loaded = Person[person._id]
        assert len(loaded.get_relations("works_in", "Department")) == 1

    def test_entity_alias(self):
        """Test entity lookup by alias (__alias__ functionality)."""
        # Create a person with a specific name
        person = Person(name="Jane", age=28)

        # Look up by ID
        by_id = Person[person._id]
        assert by_id is not None
        assert by_id._id == person._id

        # Look up by the aliased field (name)
        by_alias = Person["Jane"]
        assert by_alias is not None
        assert by_alias._id == person._id

        # Make sure they're the same entity
        assert by_id == by_alias

        # Create a numeric ID person to test numeric ID handling
        numeric_person = Person(_id="42", name="NumericTest", age=35)

        # Look up by numeric and string ID
        assert Person[42] == numeric_person
        assert Person["42"] == numeric_person

        # Verify alias lookup still works
        assert Person["NumericTest"] == numeric_person

        # Test that alias lookup returns None after entity deletion

        # Delete the first person (Jane)
        person.delete()

        # Verify that lookup by ID returns None
        assert Person[person._id] is None

        # Verify that lookup by alias (name) returns None
        assert Person["Jane"] is None

    def test_instances_basic(self):
        """Test basic functionality of instances() method."""
        # Create multiple persons
        person1 = Person(name="John", age=30)
        person2 = Person(name="Jane", age=25)

        # Retrieve all Person instances by explicitly calling instances()
        persons = Person.instances()

        # Check that we have the correct number of instances
        print("len(persons)", len(persons))
        assert len(persons) == 2

        # Check that the instances match the saved persons
        saved_ids = {person1._id, person2._id}
        retrieved_ids = {p._id for p in persons}
        assert saved_ids == retrieved_ids

    def test_instances_with_type_name(self):
        """Test instances() method with explicit type name."""
        # Create a Person and a Department
        Person(name="John", age=30)
        Department(name="Engineering")

        # Retrieve Person instances using explicit type name by calling instances()
        persons = Person.instances()
        departments = Department.instances()

        # Check that we have the correct number of instances for each type
        print("len(persons)", len(persons))
        assert len(persons) == 1
        assert len(departments) == 1

        # Check that the instances are of the correct type
        assert all(isinstance(p, Person) for p in persons)
        assert all(isinstance(d, Department) for d in departments)

    def test_instances_empty(self):
        """Test instances() method when no instances exist."""

        # Create a new entity type
        class NewEntity(Entity):
            pass

        # Retrieve instances by calling instances()
        instances = NewEntity.instances()

        # Check that no instances are returned
        assert len(instances) == 0

    def test_instances_with_multiple_types(self):
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

    def test_entity_inheritance(self):
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

    def test_load_some_basic(self):
        """Test basic load_some functionality."""
        # Create 15 test entities
        for i in range(15):
            Person(name=f"Person{i}")

        # Test first page (entities 1-10)
        first_page = Person.load_some(from_id=1, count=10)
        assert len(first_page) == 10
        assert first_page[0].name == "Person0"
        assert first_page[9].name == "Person9"

        # Test second page (entities 11-15)
        second_page = Person.load_some(from_id=11, count=10)
        assert len(second_page) == 5
        assert second_page[0].name == "Person10"
        assert second_page[4].name == "Person14"

        # Test with different count
        custom_page = Person.load_some(from_id=1, count=5)
        assert len(custom_page) == 5
        assert custom_page[0].name == "Person0"
        assert custom_page[4].name == "Person4"

    def test_load_some_edge_cases(self):
        """Test edge cases in load_some."""
        # Create 5 test entities
        for i in range(5):
            Person(name=f"Person{i}")

        # Test loading from start
        first_page = Person.load_some(from_id=1, count=10)
        assert len(first_page) == 5
        assert first_page[0].name == "Person0"
        assert first_page[4].name == "Person4"

        # Test loading from beyond last entity
        empty_page = Person.load_some(from_id=6, count=10)
        assert len(empty_page) == 0

    def test_load_some_errors(self):
        """Test load_some error handling."""
        # Test negative from_id
        try:
            Person.load_some(from_id=-1, count=10)
            assert False, "Should have raised ValueError for negative from_id"
        except ValueError as e:
            assert str(e) == "from_id must be at least 1"

        # Test zero count
        try:
            Person.load_some(from_id=1, count=0)
            assert False, "Should have raised ValueError for zero count"
        except ValueError as e:
            assert str(e) == "count must be at least 1"

        # Test negative count
        try:
            Person.load_some(from_id=1, count=-1)
            assert False, "Should have raised ValueError for negative count"
        except ValueError as e:
            assert str(e) == "count must be at least 1"

    def test_load_some_with_deleted_entities(self):
        """Test load_some with deleted entities."""
        # Create 10 test entities
        for i in range(10):
            Person(name=f"Person{i}")

        # Delete entities 5 and 6
        Person[5].delete()
        Person[6].delete()

        # Test loading from start (should skip deleted entities)
        first_page = Person.load_some(from_id=1, count=10)
        assert len(first_page) == 8
        assert first_page[0].name == "Person0"
        assert first_page[5].name == "Person7"

        # Test loading from beyond last entity
        empty_page = Person.load_some(from_id=11, count=10)
        assert len(empty_page) == 0

    def test_count_method(self):
        """Test the count method."""
        # Test count with no entities
        assert Person.count() == 0

        # Create some entities
        for i in range(5):
            Person(name=f"Person{i}", age=20 + i)
        assert Person.count() == 5

        # Delete some entities
        Person[1].delete()
        Person[2].delete()
        assert Person.count() == 3  # Count should still be 5 as it uses last_id

        # Create more entities
        for i in range(5, 10):
            Person(name=f"Person{i}", age=20 + i)
        assert Person.count() == 8


def run(test_name: str = None, test_var: str = None):
    tester = Tester(TestEntity)
    return tester.run_tests()


if __name__ == "__main__":
    exit(run())
