"""Example script showing timestamp and ownership features with properties."""

import os

from kybra_simple_db import *

# Set up database
db = Database(MemoryStorage())
Database._instance = db


class User(Entity, TimestampedMixin):
    """User entity with properties and timestamp tracking."""

    name = String(min_length=2, max_length=50)
    age = Integer(min_value=0, max_value=150)


# Set up system time for demonstration
system_time = SystemTime.get_instance()
system_time.set_time(1000000)  # Set initial time in milliseconds
print("Initial time:", system_time.format_timestamp(system_time.get_time()))

# Create a user as 'system'
user = User(name="Test User")
print("\nCreated user:")
print("- Name:", user.name)
print("- Age:", user.age)
print("- Created at:", system_time.format_timestamp(user._timestamp_created))
print("- Updated at:", system_time.format_timestamp(user._timestamp_updated))
print("- Creator:", user._creator)
print("- Owner:", user._owner)

# Update as a different user
os.environ["CALLER_ID"] = "alice"
system_time.advance_time(
    60000
)  # Advance time by 1 minute (60 seconds = 60,000 milliseconds)
print("\nTrying to update as alice...")
try:
    user._save()
except PermissionError as e:
    print("Error:", str(e))

# Change owner and try again
print("\nChanging owner to alice...")
user.set_owner("alice")
user.age = 31  # Type checking and validation happens automatically

print("\nAfter update:")
print("- Name:", user.name)
print("- Age:", user.age)
print("- Created at:", system_time.format_timestamp(user._timestamp_created))
print("- Updated at:", system_time.format_timestamp(user._timestamp_updated))
print("- Creator:", user._creator)
print("- Updater:", user._updater)
print("- Owner:", user._owner)

# View all data as dictionary
print("\nFull user data:")
for key, value in user.to_dict().items():
    print(f"- {key}: {value}")

# Clean up
system_time.clear_time()  # Return to using real system time
