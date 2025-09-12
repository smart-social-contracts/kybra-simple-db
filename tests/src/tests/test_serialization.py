"""Test serialization format for different relation types."""

from kybra_simple_db import (
    Database,
    Entity,
    String,
    OneToOne,
    OneToMany,
    ManyToOne,
    ManyToMany,
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


def test_serialization_format():
    """Test that relations are serialized in the correct format."""
    Database.get_instance().clear()
    
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
    assert isinstance(parent_data["children"], list), "OneToMany should serialize as list"
    assert parent_data["children"] == [child1._id], f"Expected ['{child1._id}'], got {parent_data['children']}"
    
    # OneToOne should be a single value
    assert isinstance(parent_data["favorite_child"], str), "OneToOne should serialize as single value"
    assert parent_data["favorite_child"] == child1._id, f"Expected '{child1._id}', got {parent_data['favorite_child']}"
    
    # ManyToOne should be a single value
    assert isinstance(child1_data["parent"], str), "ManyToOne should serialize as single value"
    assert child1_data["parent"] == parent._id, f"Expected '{parent._id}', got {child1_data['parent']}"
    
    # ManyToMany should always be a list, even with single item
    assert isinstance(child1_data["siblings"], list), "ManyToMany should serialize as list"
    assert child1_data["siblings"] == [child2._id], f"Expected ['{child2._id}'], got {child1_data['siblings']}"
    
    # Test string representation of serialized data
    parent_str = str(parent_data)
    child1_str = str(child1_data)
    
    # Verify OneToMany appears as list in string format
    assert f"'children': ['{child1._id}']" in parent_str, f"OneToMany should appear as list in string: {parent_str}"
    
    # Verify OneToOne appears as single value in string format
    assert f"'favorite_child': '{child1._id}'" in parent_str, f"OneToOne should appear as single value in string: {parent_str}"
    
    # Verify ManyToOne appears as single value in string format
    assert f"'parent': '{parent._id}'" in child1_str, f"ManyToOne should appear as single value in string: {child1_str}"
    
    # Verify ManyToMany appears as list in string format
    assert f"'siblings': ['{child2._id}']" in child1_str, f"ManyToMany should appear as list in string: {child1_str}"
    
    # Test with multiple items
    child3 = Child(name="David")
    parent.children = [child1, child3]  # OneToMany with multiple items
    child1.siblings = [child2, child3]  # ManyToMany with multiple items
    
    parent_data = parent.serialize()
    child1_data = child1.serialize()
    
    # Should still be lists
    assert isinstance(parent_data["children"], list), "OneToMany should serialize as list"
    assert len(parent_data["children"]) == 2, "OneToMany should contain both children"
    
    assert isinstance(child1_data["siblings"], list), "ManyToMany should serialize as list"
    assert len(child1_data["siblings"]) == 2, "ManyToMany should contain both siblings"

    assert str(parent_data) == "{'_type': 'Parent', '_id': '1', 'name': 'Alice', 'children': ['1', '3'], 'favorite_child': '1'}"
    assert str(child1_data) == "{'_type': 'Child', '_id': '1', 'name': 'Bob', 'parent': '1', 'favorite_parent': '1', 'siblings': ['2', '3']}"


def test_deserialization():
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
    
    try:
        Parent.deserialize({"_type": "Parent", "name": "Test"})
        assert False, "Should have raised ValueError for missing _id"
    except ValueError as e:
        assert "must contain '_id' field" in str(e)


def test_round_trip_serialization():
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
    recreated_child3 = Child.deserialize(child3_data)
    recreated_child2 = Child.deserialize(child2_data)
    recreated_child1 = Child.deserialize(child1_data)
    recreated_parent = Parent.deserialize(parent_data)
    
    # Verify the recreated entities have the same serialized output
    recreated_parent_data = recreated_parent.serialize()
    recreated_child1_data = recreated_child1.serialize()
    
    print(f"Original parent: {parent_data}")
    print(f"Recreated parent: {recreated_parent_data}")
    print(f"Original child1: {child1_data}")
    print(f"Recreated child1: {recreated_child1_data}")
    
    assert recreated_parent.serialize() == parent_data
    assert recreated_child1.serialize() == child1_data
    assert recreated_child2.serialize() == child2_data
    assert recreated_child3.serialize() == child3_data


if __name__ == "__main__":
    test_serialization_format()
    test_deserialization()
    # test_round_trip_serialization()
    print("✅ All serialization and deserialization tests passed!")
