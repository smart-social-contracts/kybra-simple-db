"""Tests for entity properties."""

from tester import Tester

from kybra_simple_db import *


class Person(Entity):
    """Example entity with property definitions."""

    name = String(min_length=2, max_length=50)
    age = Integer(min_value=0, max_value=150)
    height = Float(min_value=0.0, max_value=3.0)
    is_active = Boolean(default=True)


class PersonWithRelations(Entity):
    """Example entity with relation properties."""

    name = String(min_length=2, max_length=50)
    friends = ManyToMany(
        ["PersonWithRelations"], "friends"
    )  # Self-referential many-to-many relationship


class TestProperties:
    def test_property_types(self):
        """Test that properties enforce correct types."""
        person = Person(name="John")

        # String property
        person.name = "John"
        assert person.name == "John"

        Tester.assert_raises(TypeError, lambda: setattr(person, "name", 123))

        Tester.assert_raises(
            ValueError, lambda: setattr(person, "name", "A")
        )  # Too short

        # Integer property
        person.age = 30
        assert person.age == 30

        person.age = "25"  # Should auto-convert string to int
        assert person.age == 25
        assert isinstance(person.age, int)

        Tester.assert_raises(ValueError, lambda: setattr(person, "age", -1))

        # Float property
        person.height = 1.75
        assert person.height == 1.75

        person.height = "1.8"  # Should auto-convert string to float
        assert person.height == 1.8
        assert isinstance(person.height, float)

        Tester.assert_raises(ValueError, lambda: setattr(person, "height", 4.0))

        # Boolean property
        assert person.is_active is True  # Default value

        person.is_active = False
        assert person.is_active is False

        person.is_active = "true"  # Should convert to bool
        assert person.is_active is True

    def test_property_persistence(self):
        """Test that properties are correctly saved and loaded."""
        person = Person(name="John")
        person.name = "John"
        person.age = 30
        person.height = 1.75
        person.is_active = True

        # Load the person and verify properties
        loaded = Person.load(person._id)
        assert loaded.name == "John"
        assert loaded.age == 30
        assert loaded.height == 1.75
        assert loaded.is_active is True

    def test_property_defaults(self):
        """Test that property defaults work correctly."""
        person = Person()
        assert person.name is None  # No default
        assert person.age is None  # No default
        assert person.height is None  # No default
        assert person.is_active is True  # Has default

    def test_relation_properties(self):
        """Test that relation properties work correctly."""
        person1 = PersonWithRelations(name="Alice")
        person1.name = "Alice"

        person2 = PersonWithRelations(name="Bob")
        person2.name = "Bob"

        person3 = PersonWithRelations(name="Charlie")
        person3.name = "Charlie"

        # Set friends using property
        person1.friends = [person2, person3]

        # Get friends using property
        friends = person1.friends
        assert len(friends) == 2
        assert person2 in friends
        assert person3 in friends

        # Check bidirectional relationship
        assert person1 in person2.friends
        assert person1 in person3.friends

        # Test setting single entity
        person1.friends = person2  # Should work with single entity too
        assert len(person1.friends) == 1
        assert person2 in person1.friends
        assert person3 not in person1.friends

        # Save and load
        person1_id = person1._id
        person2_id = person2._id

        # Clear cache
        PersonWithRelations._instances = {}

        # Load and verify relations persist
        loaded1 = PersonWithRelations.load(person1_id)
        loaded2 = PersonWithRelations.load(person2_id)

        assert loaded2 in loaded1.friends
        assert loaded1 in loaded2.friends


def run(test_name: str = None, test_var: str = None):
    Database.get_instance().clear()
    tester = Tester(TestProperties)
    return tester.run_tests()


if __name__ == "__main__":
    exit(run())
