"""Example script showing:

1. Timestamp and ownership features with properties.
2. Audit trail
3. Entity Inheritance
"""

import os

from kybra_simple_logging import get_logger

import kybra_simple_db as ksdb

logger = get_logger(__name__)


def run(test_name: str = None, test_var: str = None):

    class User(ksdb.Entity, ksdb.TimestampedMixin):
        """User entity with properties and timestamp tracking."""

        name = ksdb.String(min_length=2, max_length=50)
        age = ksdb.Integer(min_value=0, max_value=150)

    # Set up system time for demonstration
    system_time = ksdb.SystemTime.get_instance()
    system_time.set_time(1742316676123)  # Set initial time in milliseconds

    # Create a user as 'system'
    user = User(name="Test User")
    assert user.name == "Test User"
    assert user.age is None  # No age set initially
    assert user._creator == "system"  # Default creator
    assert user._owner == "system"  # Default owner

    # Update as a different user
    os.environ["CALLER_ID"] = "alice"
    system_time.advance_time(60000)  # Advance time by 1 minute (60,000 milliseconds)
    try:
        user._save()
        assert False, "PermissionError should have been raised"
    except PermissionError:
        pass  # Expected behavior

    # Change owner and try again
    user.set_owner("alice")
    user.age = 31  # Type checking and validation happens automatically
    assert user._owner == "alice"
    assert user.age == 31

    # Now save should succeed
    user._save()
    assert user._updater == "alice"

    # Get user data dictionary
    user_dict = user.serialize()
    assert "name" in user_dict
    assert user_dict["name"] == "Test User"
    assert user_dict["age"] == 31

    # Check that timestamps and ownership are tracked correctly
    assert user._creator == "system"
    assert user._owner == "alice"

    # Clean up
    system_time.clear_time()  # Return to using real system time

    return 0


if __name__ == "__main__":
    ksdb.Database.get_instance().clear()
    exit(run())
