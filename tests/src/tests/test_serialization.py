"""Test serialization format for different relation types."""

from tester import Tester

from kybra_simple_db import (
    Database,
    Entity,
    ManyToMany,
    ManyToOne,
    OneToMany,
    OneToOne,
    String,
)


class Parent(Entity):
    name = String()
    children = OneToMany("Child", "parent")  # Should always be list
    favorite_child = OneToOne("Child", "favorite_parent")  # Should be single value


class Child(Entity):
    name = String()
    parent = ManyToOne("Parent", "children")  # Should be single value
    favorite_parent = OneToOne("Parent", "favorite_child")  # Should be single value
    siblings = ManyToMany("Child", "siblings")  # Should always be list


class TestSerialization:
    def setUp(self):
        """Reset Entity class variables before each test."""
        Database.get_instance().clear()

    def test_serialization_format(self):
        """Test that relations are serialized in the correct format."""

        # Create entities
        parent = Parent(name="Alice")
        child1 = Child(name="Bob")
        child2 = Child(name="Charlie")

        # Set up relations
        parent.children = [child1]  # OneToMany with single item
        parent.favorite_child = child1  # OneToOne
        child1.siblings = [child2]  # ManyToMany with single item

        # Test serialization
        parent_data = parent.serialize()
        child1_data = child1.serialize()

        # OneToMany should always be a list, even with single item
        assert isinstance(
            parent_data["children"], list
        ), "OneToMany should serialize as list"
        assert parent_data["children"] == [
            child1._id
        ], f"Expected ['{child1._id}'], got {parent_data['children']}"

        # OneToOne should be a single value
        assert isinstance(
            parent_data["favorite_child"], str
        ), "OneToOne should serialize as single value"
        assert (
            parent_data["favorite_child"] == child1._id
        ), f"Expected '{child1._id}', got {parent_data['favorite_child']}"

        # ManyToOne should be a single value
        assert isinstance(
            child1_data["parent"], str
        ), "ManyToOne should serialize as single value"
        assert (
            child1_data["parent"] == parent._id
        ), f"Expected '{parent._id}', got {child1_data['parent']}"

        # ManyToMany should always be a list, even with single item
        assert isinstance(
            child1_data["siblings"], list
        ), "ManyToMany should serialize as list"
        assert child1_data["siblings"] == [
            child2._id
        ], f"Expected ['{child2._id}'], got {child1_data['siblings']}"

        # Test string representation of serialized data
        parent_str = str(parent_data)
        child1_str = str(child1_data)

        # Verify OneToMany appears as list in string format
        assert (
            f"'children': ['{child1._id}']" in parent_str
        ), f"OneToMany should appear as list in string: {parent_str}"

        # Verify OneToOne appears as single value in string format
        assert (
            f"'favorite_child': '{child1._id}'" in parent_str
        ), f"OneToOne should appear as single value in string: {parent_str}"

        # Verify ManyToOne appears as single value in string format
        assert (
            f"'parent': '{parent._id}'" in child1_str
        ), f"ManyToOne should appear as single value in string: {child1_str}"

        # Verify ManyToMany appears as list in string format
        assert (
            f"'siblings': ['{child2._id}']" in child1_str
        ), f"ManyToMany should appear as list in string: {child1_str}"

        # Test with multiple items
        child3 = Child(name="David")
        parent.children = [child1, child3]  # OneToMany with multiple items
        child1.siblings = [child2, child3]  # ManyToMany with multiple items

        parent_data = parent.serialize()
        child1_data = child1.serialize()

        # Should still be lists
        assert isinstance(
            parent_data["children"], list
        ), "OneToMany should serialize as list"
        assert (
            len(parent_data["children"]) == 2
        ), "OneToMany should contain both children"

        assert isinstance(
            child1_data["siblings"], list
        ), "ManyToMany should serialize as list"
        assert (
            len(child1_data["siblings"]) == 2
        ), "ManyToMany should contain both siblings"

        assert (
            str(parent_data)
            == "{'_type': 'Parent', '_id': '1', 'name': 'Alice', 'children': ['1', '3'], 'favorite_child': '1'}"
        )
        assert (
            str(child1_data)
            == "{'_type': 'Child', '_id': '1', 'name': 'Bob', 'parent': '1', 'favorite_parent': '1', 'siblings': ['2', '3']}"
        )

    def test_deserialization(self):
        """Test that entities can be reconstructed from serialized data."""
        Database.get_instance().clear()

        # Create original entities
        parent = Parent(name="Alice")
        child1 = Child(name="Bob")
        child2 = Child(name="Charlie")

        # Set up relations
        parent.children = [child1]
        parent.favorite_child = child1
        child1.siblings = [child2]

        # Serialize the entities
        parent_data = parent.serialize()
        child1_data = child1.serialize()

        # Clear database to test deserialization
        Database.get_instance().clear()

        # Recreate entities from serialized data
        # Note: We need to create all entities first before setting relations
        recreated_parent = Parent.deserialize(parent_data)
        recreated_child1 = Child.deserialize(child1_data)

        # Verify basic properties
        assert recreated_parent.name == "Alice"
        assert recreated_parent._id == "1"
        assert recreated_child1.name == "Bob"
        assert recreated_child1._id == "1"

        # Test error cases
        try:
            Parent.deserialize({"invalid": "data"})
            assert False, "Should have raised ValueError for missing _type"
        except ValueError as e:
            assert "must contain '_type' field" in str(e)

        try:
            Parent.deserialize({"_type": "Child", "_id": "1", "name": "Test"})
            assert False, "Should have raised ValueError for type mismatch"
        except ValueError as e:
            assert "Entity type mismatch" in str(e)

        # Test that missing _id now creates a new entity (upsert behavior)
        Database.get_instance().clear()  # Clear to avoid conflicts
        result = Parent.deserialize({"_type": "Parent", "name": "Test"})
        assert result is not None, "Should create new entity when _id is missing"
        assert result.name == "Test", "Should set name property"
        assert result._id is not None, "Should auto-generate _id"

    def test_round_trip_serialization(self):
        """Test that serialize -> deserialize produces equivalent entities."""
        Database.get_instance().clear()

        # Create entities with complex relationships
        parent = Parent(name="Alice")
        child1 = Child(name="Bob")
        child2 = Child(name="Charlie")
        child3 = Child(name="David")

        # Set up complex relations
        parent.children = [child1, child2]
        parent.favorite_child = child1
        child1.siblings = [child2, child3]
        child2.siblings = [child1, child3]

        # Serialize all entities
        parent_data = parent.serialize()
        child1_data = child1.serialize()
        child2_data = child2.serialize()
        child3_data = child3.serialize()

        # Clear and recreate from serialized data
        Database.get_instance().clear()

        # Recreate entities (order matters for relations)
        Child.deserialize(child3_data)
        Child.deserialize(child2_data)
        recreated_child1 = Child.deserialize(child1_data)
        recreated_parent = Parent.deserialize(parent_data)

        # Debug: Check pending relations before resolving
        print(
            f"Parent pending relations: {getattr(recreated_parent, '_pending_relations', {})}"
        )
        print(
            f"Child1 pending relations: {getattr(recreated_child1, '_pending_relations', {})}"
        )

        # Debug: Check what entities exist in database
        print(f"Parent instances: {[p._id for p in Parent.instances()]}")
        print(f"Child instances: {[c._id for c in Child.instances()]}")

        # Resolve all pending relations after all entities are created
        from kybra_simple_db import Entity

        # Manual resolution test for parent
        if hasattr(recreated_parent, "_pending_relations"):
            print("Manually resolving parent relations...")
            for key, value in recreated_parent._pending_relations.items():
                prop = getattr(Parent, key, None)
                print(f"  {key}: prop={prop}, value={value}")
                if prop:
                    print(f"  Property type: {type(prop)}")
                    print(f"  Entity types: {getattr(prop, 'entity_types', None)}")
                    print(
                        f"  Entity types type: {type(getattr(prop, 'entity_types', None))}"
                    )
                    if hasattr(prop, "entity_types"):
                        print(
                            f"  First entity type: {prop.entity_types[0] if prop.entity_types else 'None'}"
                        )

        Entity.resolve_pending_relations()

        # Debug: Check after resolving
        print(f"Parent relations after resolve: {recreated_parent._relations}")
        print(f"Child1 relations after resolve: {recreated_child1._relations}")

        # Verify the recreated entities have the same serialized output
        recreated_parent_data = recreated_parent.serialize()
        recreated_child1_data = recreated_child1.serialize()

        print(f"Original parent: {parent_data}")
        print(f"Recreated parent: {recreated_parent_data}")
        print(f"Original child1: {child1_data}")
        print(f"Recreated child1: {recreated_child1_data}")

        # Verify that serialized data matches (allowing for different ordering in many-to-many relations)
        assert (
            recreated_parent_data == parent_data
        ), f"Parent data mismatch:\nOriginal: {parent_data}\nRecreated: {recreated_parent_data}"

        # For child1, check each field individually to handle list ordering
        for key, value in child1_data.items():
            if key == "siblings":  # ManyToMany relation - check set equality
                assert set(recreated_child1_data[key]) == set(
                    value
                ), f"Siblings mismatch: {recreated_child1_data[key]} != {value}"
            else:
                assert (
                    recreated_child1_data[key] == value
                ), f"Field {key} mismatch: {recreated_child1_data[key]} != {value}"

        # Verify basic properties are preserved
        assert recreated_parent.name == "Alice"
        assert recreated_child1.name == "Bob"

        # Verify relations are properly restored
        assert len(recreated_parent.children) == 2, "Parent should have 2 children"
        assert (
            recreated_parent.favorite_child is not None
        ), "Parent should have a favorite child"
        assert len(recreated_child1.siblings) == 2, "Child1 should have 2 siblings"

    def test_generic_deserialization(self):
        """Test that Entity.deserialize() works without knowing the entity type."""
        Database.get_instance().clear()

        # Create entities
        parent = Parent(name="Alice")
        child = Child(name="Bob")
        parent.children = [child]

        # Serialize entities
        parent_data = parent.serialize()
        child_data = child.serialize()

        # Clear database
        Database.get_instance().clear()

        # Test generic deserialization using Entity.deserialize()
        from kybra_simple_db import Entity

        recreated_parent = Entity.deserialize(parent_data)
        recreated_child = Entity.deserialize(child_data)

        # Verify types and properties
        assert isinstance(recreated_parent, Parent), "Should recreate Parent instance"
        assert isinstance(recreated_child, Child), "Should recreate Child instance"
        assert recreated_parent.name == "Alice"
        assert recreated_child.name == "Bob"
        assert recreated_parent._id == "1"
        assert recreated_child._id == "1"

        # Test the round-trip pattern: student = Entity.deserialize(student.serialize())
        Database.get_instance().clear()
        original = Parent(name="Test")
        roundtrip = Entity.deserialize(original.serialize())

        assert isinstance(roundtrip, Parent), "Round-trip should preserve type"
        assert roundtrip.name == "Test", "Round-trip should preserve properties"
        assert roundtrip._id == original._id, "Round-trip should preserve ID"

        # Test error cases
        try:
            Entity.deserialize({"invalid": "data"})
            assert False, "Should raise ValueError for missing _type"
        except ValueError as e:
            assert "must contain '_type' field" in str(e)

        try:
            Entity.deserialize({"_type": "NonExistentEntity", "_id": "1"})
            assert False, "Should raise ValueError for unknown entity type"
        except ValueError as e:
            assert "Unknown entity type" in str(e)

    def test_upsert_functionality(self):
        """Test the upsert functionality of Entity.deserialize method."""
        Database.get_instance().clear()

        # Test 1: Create new entity when no _id provided
        data = {"_type": "Parent", "name": "John"}
        parent = Parent.deserialize(data)

        assert parent is not None
        assert parent.name == "John"
        assert parent._id == "1"  # Auto-generated ID
        assert Parent.count() == 1

        # Test 2: Create new entity when provided _id doesn't exist
        data = {"_type": "Parent", "_id": "999", "name": "Jane"}
        parent2 = Parent.deserialize(data)

        assert parent2 is not None
        assert parent2.name == "Jane"
        assert (
            parent2._id == "999"
        )  # Now preserves provided _id when creating new entity
        assert Parent.count() == 2

        # Test 3: Update existing entity by _id
        original_id = parent._id
        data = {"_type": "Parent", "_id": original_id, "name": "John Updated"}
        updated = Parent.deserialize(data)

        assert updated is not None
        assert updated._id == original_id  # Same ID
        assert updated.name == "John Updated"
        assert Parent.count() == 2  # Count didn't increase
        assert updated is parent  # Same entity instance due to registry

        # Test 4: Partial update (merge mode)
        # First create entity with multiple properties
        Database.get_instance().clear()

        class TestEntity(Entity):
            name = String()
            description = String()

        original = TestEntity(name="Test", description="Original description")
        original_id = original._id

        # Update only one field
        data = {"_type": "TestEntity", "_id": original_id, "name": "Updated Test"}
        updated = TestEntity.deserialize(data)

        assert updated._id == original_id
        assert updated.name == "Updated Test"  # Updated
        assert updated.description == "Original description"  # Unchanged
        assert TestEntity.count() == 1

    def test_upsert_with_alias(self):
        """Test upsert functionality with alias fields."""
        Database.get_instance().clear()

        # Create entity class with alias
        class User(Entity):
            __alias__ = "name"
            name = String()
            age = String()

        # Test 1: Create new entity with alias (no existing match)
        data = {"_type": "User", "name": "Alice", "age": "30"}
        user = User.deserialize(data)

        assert user is not None
        assert user.name == "Alice"
        assert user.age == "30"
        assert user._id == "1"
        assert User.count() == 1

        # Test 2: Update existing entity by alias (no _id provided)
        data = {"_type": "User", "name": "Alice", "age": "31"}
        updated = User.deserialize(data)

        assert updated is not None
        assert updated._id == "1"  # Same ID
        assert updated.name == "Alice"  # Same name
        assert updated.age == "31"  # Updated age
        assert User.count() == 1  # Count didn't increase
        assert updated is user  # Same entity instance

        # Test 3: Create new entity when alias doesn't match
        data = {"_type": "User", "name": "Bob", "age": "25"}
        bob = User.deserialize(data)

        assert bob is not None
        assert bob.name == "Bob"
        assert bob.age == "25"
        assert bob._id == "2"
        assert User.count() == 2

        # Test 4: Update alias field itself
        original_id = user._id
        data = {"_type": "User", "_id": original_id, "name": "Alicia", "age": "32"}
        updated = User.deserialize(data)

        assert updated._id == original_id
        assert updated.name == "Alicia"
        assert updated.age == "32"

        # Verify old alias no longer works
        assert User["Alice"] is None

        # Verify new alias works
        found = User["Alicia"]
        assert found is not None
        assert found._id == original_id

    def test_upsert_with_relations(self):
        """Test that upsert handles relations correctly via pending relations."""
        Database.get_instance().clear()

        # Create entities first
        parent = Parent(name="Alice")
        child = Child(name="Bob")

        # Test create with relations
        data = {
            "_type": "Child",
            "name": "Charlie",
            "parent": parent._id,  # This should go to pending relations
        }
        charlie = Child.deserialize(data)

        assert charlie.name == "Charlie"
        assert hasattr(charlie, "_pending_relations")
        assert "parent" in charlie._pending_relations
        assert charlie._pending_relations["parent"] == parent._id

        # Test update with relations
        update_data = {
            "_type": "Child",
            "_id": child._id,
            "name": "Bob Updated",
            "parent": parent._id,
        }
        updated_child = Child.deserialize(update_data)

        assert updated_child.name == "Bob Updated"
        assert hasattr(updated_child, "_pending_relations")
        assert "parent" in updated_child._pending_relations
        assert updated_child._pending_relations["parent"] == parent._id
        assert updated_child is child  # Same instance


def run(test_name: str = None, test_var: str = None):
    tester = Tester(TestSerialization)
    return tester.run_tests()


if __name__ == "__main__":
    exit(run())
