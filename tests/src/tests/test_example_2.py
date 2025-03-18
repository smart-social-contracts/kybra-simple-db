"""Example script showing timestamp and ownership features with properties."""

import os

import kybra_simple_db as ksdb


def run():
    log = ksdb.get_logger()

    class User(ksdb.Entity, ksdb.TimestampedMixin):
        """User entity with properties and timestamp tracking."""

        name = ksdb.String(min_length=2, max_length=50)
        age = ksdb.Integer(min_value=0, max_value=150)

    # Set up system time for demonstration
    system_time = ksdb.SystemTime.get_instance()
    system_time.set_time(1000000)  # Set initial time in milliseconds
    log("Initial time:", system_time.format_timestamp(system_time.get_time()))

    # Create a user as 'system'
    user = User(name="Test User")
    log("\nCreated user:")
    log("- Name:", user.name)
    log("- Age:", user.age)
    log("- Created at:", system_time.format_timestamp(user._timestamp_created))
    log("- Updated at:", system_time.format_timestamp(user._timestamp_updated))
    log("- Creator:", user._creator)
    log("- Owner:", user._owner)

    # Update as a different user
    os.environ["CALLER_ID"] = "alice"
    system_time.advance_time(
        60000
    )  # Advance time by 1 minute (60 seconds = 60,000 milliseconds)
    log("\nTrying to update as alice...")
    try:
        user._save()
    except PermissionError as e:
        log("Error:", str(e))

    # Change owner and try again
    log("\nChanging owner to alice...")
    user.set_owner("alice")
    user.age = 31  # Type checking and validation happens automatically

    log("\nAfter update:")
    log("- Name:", user.name)
    log("- Age:", user.age)
    log("- Created at:", system_time.format_timestamp(user._timestamp_created))
    log("- Updated at:", system_time.format_timestamp(user._timestamp_updated))
    log("- Creator:", user._creator)
    log("- Updater:", user._updater)
    log("- Owner:", user._owner)

    # View all data as dictionary
    log("\nFull user data:")
    for key, value in user.to_dict().items():
        log(f"- {key}: {value}")

    # Clean up
    system_time.clear_time()  # Return to using real system time

    return 0


if __name__ == "__main__":
    exit(run())
