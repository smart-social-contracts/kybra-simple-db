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
    logger.debug(f"Initial time: {system_time.print()}")

    # Create a user as 'system'
    user = User(name="Test User")
    logger.debug("\nCreated user:")
    logger.debug(f"- Name: {user.name}")
    logger.debug(f"- Age: {user.age}")
    logger.debug(
        f"- Created at: {system_time.format_timestamp(user._timestamp_created)}"
    )
    logger.debug(
        f"- Updated at: {system_time.format_timestamp(user._timestamp_updated)}"
    )
    logger.debug(f"- Creator: {user._creator}")
    logger.debug(f"- Owner: {user._owner}")

    # Update as a different user
    os.environ["CALLER_ID"] = "alice"
    system_time.advance_time(60000)  # Advance time by 1 minute (60,000 milliseconds)
    logger.debug("\nTrying to update as alice...")
    try:
        user._save()
    except PermissionError as e:
        logger.debug(f"Error: {str(e)}")

    # Change owner and try again
    logger.debug("\nChanging owner to alice...")
    user.set_owner("alice")
    user.age = 31  # Type checking and validation happens automatically

    logger.debug("\nAfter update:")
    logger.debug(f"- Name: {user.name}")
    logger.debug(f"- Age: {user.age}")
    logger.debug(
        f"- Created at: {system_time.format_timestamp(user._timestamp_created)}"
    )
    logger.debug(
        f"- Updated at: {system_time.format_timestamp(user._timestamp_updated)}"
    )
    logger.debug(f"- Creator: {user._creator}")
    logger.debug(f"- Updater: {user._updater}")
    logger.debug(f"- Owner: {user._owner}")

    # View all data as dictionary
    logger.debug("\nFull user data:")
    for key, value in user.to_dict().items():
        logger.debug(f"- {key}: {value}")

    # Clean up
    system_time.clear_time()  # Return to using real system time

    return 0


if __name__ == "__main__":
    exit(run())
