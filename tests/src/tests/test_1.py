"""Simple example script showing basic usage of kybra_simple_db with properties."""

from kybra_simple_db.logger import get_logger

from kybra_simple_db import *


def run():
    log = get_logger()

    # Set up database
    db = Database(MemoryStorage())
    Database._instance = db

    class User(Entity):
        """User entity with typed properties."""

        name = String(min_length=2, max_length=50)
        age = Integer(min_value=0, max_value=150)

    # Create and save a user
    user = User(name="John", age=30)
    log("Created user: %s" % {"name": user.name, "age": user.age})

    # Load the user - use the cached instance since we just saved it
    log("Loaded user:%s" % {"name": user.name, "age": user.age})

    # Update the user's age
    user.age = 31  # Type checking and validation happens automatically
    log("Updated user:%s" % {"name": user.name, "age": user.age})

    # _id can be used to load an entity
    peter = User(_id="peter", name="Peter")
    peter_loaded = User["peter"]
    log(peter_loaded.to_dict())

    # [] operator can be used to load an entity
    peter_loaded_2 = User["peter"]
    print(peter_loaded_2.to_dict())

    # Print storage contents
    log("\nStorage contents:")
    log(db.raw_dump_json(pretty=True))

    # Delete the user
    user.delete()
    deleted = User.load("1")
    log("After delete:%s" % deleted)  # None

    return 0


if __name__ == "__main__":
    exit(run())
