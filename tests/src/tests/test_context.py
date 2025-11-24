"""Tests for context-based caller management."""

import pytest

from kybra_simple_db import Database, Entity, String
from kybra_simple_db.context import get_caller_id, set_caller_id
from kybra_simple_db.mixins import TimestampedMixin


def test_get_caller_id_default():
    """Default caller ID is 'system'."""
    # Clear any previous state
    set_caller_id("system")
    assert get_caller_id() == "system"


def test_set_caller_id():
    """Can set caller ID."""
    set_caller_id("alice")
    assert get_caller_id() == "alice"

    set_caller_id("bob")
    assert get_caller_id() == "bob"

    # Reset
    set_caller_id("system")


def test_as_user_context_manager():
    """as_user context manager sets and resets caller."""
    db = Database.get_instance()
    db.clear()

    # Initial state
    assert get_caller_id() == "system"

    # Use context manager
    with db.as_user("alice"):
        assert get_caller_id() == "alice"

    # Should reset after context
    assert get_caller_id() == "system"


def test_as_user_nested():
    """Nested as_user contexts work correctly."""
    db = Database.get_instance()
    db.clear()

    set_caller_id("system")

    with db.as_user("alice"):
        assert get_caller_id() == "alice"

        with db.as_user("bob"):
            assert get_caller_id() == "bob"

        # Back to alice
        assert get_caller_id() == "alice"

    # Back to system
    assert get_caller_id() == "system"


def test_as_user_with_entity_creation():
    """Entities created in as_user context have correct owner."""
    db = Database.get_instance()
    db.clear()

    class User(Entity, TimestampedMixin):
        name = String()

    with db.as_user("alice"):
        alice_user = User(name="Alice")
        assert alice_user._owner == "alice"
        assert alice_user._creator == "alice"

    with db.as_user("bob"):
        bob_user = User(name="Bob")
        assert bob_user._owner == "bob"
        assert bob_user._creator == "bob"


def test_as_user_with_access_control():
    """Access control works with as_user context."""
    db = Database.get_instance()
    db.clear()

    class Document(Entity, TimestampedMixin):
        title = String()

        @staticmethod
        def on_event(entity, field_name, old_value, new_value, action):
            from kybra_simple_db import ACTION_DELETE, ACTION_MODIFY
            from kybra_simple_db.context import get_caller_id

            caller = get_caller_id()

            if action in (ACTION_MODIFY, ACTION_DELETE):
                if entity._owner != caller:
                    return False, None

            return True, new_value

    # Alice creates document
    with db.as_user("alice"):
        doc = Document(title="Alice's Doc")
        assert doc._owner == "alice"

        # Alice can modify her own doc
        doc.title = "Updated"
        assert doc.title == "Updated"

    # Bob cannot modify Alice's doc
    with db.as_user("bob"):
        with pytest.raises(ValueError, match="Hook rejected"):
            doc.title = "Hacked"


def test_as_user_exception_handling():
    """Context manager resets caller even if exception occurs."""
    db = Database.get_instance()
    db.clear()

    set_caller_id("system")

    try:
        with db.as_user("alice"):
            assert get_caller_id() == "alice"
            raise RuntimeError("Test error")
    except RuntimeError:
        pass

    # Should still reset to system
    assert get_caller_id() == "system"


def test_as_user_multiple_operations():
    """Multiple operations in same context use same caller."""
    db = Database.get_instance()
    db.clear()

    class Item(Entity, TimestampedMixin):
        name = String()

    with db.as_user("alice"):
        item1 = Item(name="Item 1")
        item2 = Item(name="Item 2")
        item3 = Item(name="Item 3")

        assert item1._owner == "alice"
        assert item2._owner == "alice"
        assert item3._owner == "alice"


def test_as_user_modification_tracking():
    """Modifications track correct updater when owner updates."""
    db = Database.get_instance()
    db.clear()

    class Record(Entity, TimestampedMixin):
        value = String()

    # Alice creates
    with db.as_user("alice"):
        record = Record(value="Initial")
        assert record._creator == "alice"
        assert record._updater == "alice"

        # Alice updates (same user)
        record.value = "Modified"
        assert record._creator == "alice"  # Still alice
        assert record._updater == "alice"  # Still alice

    # Bob cannot update Alice's record (ownership protection)
    with db.as_user("bob"):
        with pytest.raises(PermissionError, match="Only the owner"):
            record.value = "Unauthorized"


def test_as_user_isolation():
    """Different threads/contexts are isolated."""
    db = Database.get_instance()
    db.clear()

    class Task(Entity, TimestampedMixin):
        name = String()

    results = []

    # Simulate different contexts
    with db.as_user("user1"):
        task1 = Task(name="Task 1")
        results.append(task1._owner)

    with db.as_user("user2"):
        task2 = Task(name="Task 2")
        results.append(task2._owner)

    with db.as_user("user3"):
        task3 = Task(name="Task 3")
        results.append(task3._owner)

    assert results == ["user1", "user2", "user3"]
