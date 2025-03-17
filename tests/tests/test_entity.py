"""Tests for entity functionality in Kybra Simple DB."""

from kybra_simple_db import *


class Person(Entity):
    name = String(min_length=2, max_length=50)
    age = Integer()


class Department(Entity):
    name = String(min_length=2, max_length=50)


class TestEntity:
    def setUp(self):
        """Reset Entity class variables before each test."""
        Entity._context = set()
        Database._instance = Database(MemoryStorage())

    def test_entity_creation_and_save(self):
        """Test creating and saving an entity."""
        person = Person(name="John", age=30)
        loaded = Person[person._id]
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.name, "John")
        self.assertEqual(loaded.age, 31)

    def test_entity_update(self):
        """Test updating an entity."""
        person = Person(name="John", age=30)
        person.age = 31

        loaded = Person[person._id]
        self.assertEqual(loaded.age, 31)

    def test_entity_relations(self):
        """Test entity relations."""
        person = Person(name="John")
        dept = Department(name="IT")

        # Test adding relation
        person.add_relation("works_in", "has_employee", dept)

        # Check person's relations
        loaded_person = Person[person._id]
        loaded_dept = Department[dept._id]

        self.assertEqual(loaded_person.get_relations("works_in", "Department")[0], dept)
        self.assertEqual(loaded_dept.get_relations("has_employee", "Person")[0], person)

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
        person = Person(_id="John", age=30)

        # Load using class[id] syntax
        loaded_person = Person[person._id]
        self.assertIsNotNone(loaded_person)
        self.assertEqual(loaded_person._id, "John")
        self.assertEqual(loaded_person.age, 30)

        # Test with non-existent ID
        self.assertIsNone(Person["non_existent"])

    def test_entity_duplicate_relation(self):
        """Test handling of duplicate relations."""
        person = Person(name="John")
        dept = Department(name="IT")

        # Adding same relation twice should only create one
        person.add_relation("works_in", "has_employee", dept)
        person.add_relation("works_in", "has_employee", dept)

        loaded = Person[person._id]
        self.assertEqual(len(loaded.get_relations("works_in", "Department")), 1)

    def test_instances_basic(self):
        """Test basic functionality of instances() method."""
        # Create multiple persons
        person1 = Person(name="John", age=30)
        person2 = Person(name="Jane", age=25)

        # Retrieve all Person instances by explicitly calling instances()
        persons = Person.instances()

        # Check that we have the correct number of instances
        self.assertEqual(len(persons), 2)

        # Check that the instances match the saved persons
        saved_ids = {person1._id, person2._id}
        retrieved_ids = {p._id for p in persons}
        self.assertEqual(saved_ids, retrieved_ids)

    def test_instances_with_type_name(self):
        """Test instances() method with explicit type name."""
        # Create a Person and a Department
        Person(name="John", age=30)
        Department(name="Engineering")

        # Retrieve Person instances using explicit type name by calling instances()
        persons = Person.instances()
        departments = Department.instances()

        # Check that we have the correct number of instances for each type
        self.assertEqual(len(persons), 1)
        self.assertEqual(len(departments), 1)

        # Check that the instances are of the correct type
        self.assertTrue(all(isinstance(p, Person) for p in persons))
        self.assertTrue(all(isinstance(d, Department) for d in departments))

    def test_instances_empty(self):
        """Test instances() method when no instances exist."""

        # Create a new entity type
        class NewEntity(Entity):
            pass

        # Retrieve instances by calling instances()
        instances = NewEntity.instances()

        # Check that no instances are returned
        self.assertEqual(len(instances), 0)

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
        self.assertEqual(len(persons), 2)
        self.assertEqual(len(departments), 1)

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
        self.assertEqual(len(all_animals), 3)
        self.assertTrue(any(a.name == "Alice" for a in all_animals))
        self.assertTrue(any(a.name == "Bob" for a in all_animals))
        self.assertTrue(any(a.name == "Charlie" for a in all_animals))

        dogs = Dog.instances()
        self.assertEqual(len(dogs), 1)
        self.assertEqual(dogs[0].name, "Bob")

        cats = Cat.instances()
        self.assertEqual(len(cats), 1)
        self.assertEqual(cats[0].name, "Charlie")

        # Clean up
        animal_a.delete()
        dog_b.delete()
        cat_c.delete()


def run_tests():
    """Custom test runner to execute test functions and report results."""
    test_instance = TestEntity()
    test_methods = [getattr(test_instance, func) for func in dir(test_instance) if callable(getattr(test_instance, func)) and func.startswith('test_')]
    print("test_methods", test_methods)
    failed = 0
    for test in test_methods:
        try:
            test_instance.setUp()  # Call setUp before each test
            test()
            print(f"{test.__name__} passed")
        except Exception as e:
            print(f"{test.__name__} failed: {e}")
            failed += 1
    print(f"{failed} tests failed")
    if failed > 0:
        exit(1)


if __name__ == "__main__":
    print("Running tests...")
    run_tests()
