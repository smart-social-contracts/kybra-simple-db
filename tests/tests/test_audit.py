"""Tests for audit functionality in Kybra Simple DB."""

import json

import pytest

from kybra_simple_db import *


class TestUser(Entity, TimestampedMixin):
    """Test user entity with a name property."""

    _entity_type = "user"
    name = String()


@pytest.fixture
def system_time():
    """Set up system time for testing."""
    time = SystemTime.get_instance()
    time.set_time(1000000)  # 1000 seconds since epoch
    yield time
    time.clear_time()


@pytest.fixture
def caller_id():
    """Set up caller ID for testing."""
    import os

    os.environ["CALLER_ID"] = "system"
    yield
    del os.environ["CALLER_ID"]


@pytest.fixture
def db_audit():
    """Create and configure a memory storage for audit logs."""
    return MemoryStorage()


@pytest.fixture
def db(db_audit):
    """Create and configure the database with audit storage."""
    db = Database(db_audit=db_audit)
    Database._instance = db
    return db


def test_entity_creation_audit(db_audit, db, system_time, caller_id):
    """Test that entity creation is properly audited."""
    user = TestUser(name="Alice")

    # Get all audit logs except internal IDs
    audit_entries = [
        json.loads(db_audit.get(key))
        for key in sorted(db_audit.keys())
        if key not in ["_min_id", "_max_id"]
    ]

    # Should have one audit entry for the save
    assert len(audit_entries) == 1
    entry = audit_entries[0]

    # Check audit entry format
    assert entry[0] == "save"  # Operation type
    assert isinstance(entry[1], int)  # Timestamp
    print("entry", entry)
    assert entry[2].startswith("TestUser@")  # Entity identifier

    # Check audited data
    data = entry[3]
    assert data["_type"] == "TestUser"
    assert isinstance(data["_id"], str)
    assert data["timestamp_created"] == data["timestamp_updated"]
    assert data["creator"] == data["updater"] == "system"
    assert data["owner"] == "system"


def test_entity_update_audit(db_audit, db, system_time, caller_id):
    """Test that entity updates are properly audited."""
    user = TestUser(name="Alice")

    # Update the user with a new timestamp
    system_time.set_time(1001000)  # Advance time by 1 second
    user.name = "Alice Smith"

    # Get audit entries in chronological order
    audit_entries = [
        json.loads(db_audit.get(key))
        for key in sorted(db_audit.keys())
        if key not in ["_min_id", "_max_id"]
    ]

    # Should have two audit entries - creation and update
    assert len(audit_entries) == 2

    # First entry should be creation
    create_entry = audit_entries[0]
    assert create_entry[0] == "save"
    assert create_entry[3]["timestamp_created"] == create_entry[3]["timestamp_updated"]

    # Second entry should be update
    update_entry = audit_entries[1]
    assert update_entry[0] == "save"
    assert update_entry[3]["timestamp_updated"] > update_entry[3]["timestamp_created"]


def test_multiple_entities_audit(db_audit, db, system_time, caller_id):
    """Test audit logging with multiple entities."""
    # Create multiple users
    [TestUser(name=f"User{i}") for i in range(3)]

    # Get audit entries
    audit_entries = [
        json.loads(db_audit.get(key))
        for key in sorted(db_audit.keys())
        if key not in ["_min_id", "_max_id"]
    ]

    # Should have one entry per user
    assert len(audit_entries) == 3

    # Each entry should be for a different user
    user_ids = {entry[3]["_id"] for entry in audit_entries}
    assert len(user_ids) == 3


def test_audit_persistence(db_audit, db, system_time, caller_id):
    """Test that audit entries persist across database operations."""
    # Create and update a user
    user = TestUser(name="Alice")
    system_time.set_time(1001000)  # Advance time by 1 second
    user.name = "Alice Smith"

    # Create another user
    TestUser(name="Bob")

    # Get all audit entries
    audit_entries = [
        json.loads(db_audit.get(key))
        for key in sorted(db_audit.keys())
        if key not in ["_min_id", "_max_id"]
    ]

    # Should have three entries total
    assert len(audit_entries) == 3

    # Check chronological order
    timestamps = [entry[1] for entry in audit_entries]
    assert timestamps == sorted(timestamps)

    # Check entity references
    entity_refs = [entry[2] for entry in audit_entries]
    assert len(set(entity_refs)) == 2  # Two unique entities
