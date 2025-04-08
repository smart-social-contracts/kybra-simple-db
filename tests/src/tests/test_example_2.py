"""Example script showing:

1. timestamp and ownership features with properties.
2. Audit trail
3. Entity Inheritance
"""

import os

from kybra_simple_logging import get_logger

import kybra_simple_db as ksdb

logger = get_logger(__name__)


def run():

    class User(ksdb.Entity, ksdb.TimestampedMixin):
        """User entity with properties and timestamp tracking."""

        name = ksdb.String(min_length=2, max_length=50)
        age = ksdb.Integer(min_value=0, max_value=150)

    # from kybra_simple_db import *

    # # Create database with audit logging
    # db = Database(MemoryStorage(), MemoryStorage())

    # # Perform operations
    # db.save("user1", {"name": "John"})

    # # View audit log
    # print(db.get_audit())

    # Set up system time for demonstration
    system_time = ksdb.SystemTime.get_instance()
    system_time.set_time(1742316676123)  # Set initial time in milliseconds

    # Create a user as 'system'
    user = User(name="Test User")

    # Update as a different user
    os.environ["CALLER_ID"] = "alice"
    system_time.advance_time(60000)  # Advance time by 1 minute (60,000 milliseconds)
    try:
        user._save()
    except PermissionError:
        pass

    # Change owner and try again
    user.set_owner("alice")
    user.age = 31  # Type checking and validation happens automatically

    # Get user data dictionary
    user.to_dict()

    # Clean up
    system_time.clear_time()  # Return to using real system time

    return 0


if __name__ == "__main__":
    exit(run())
