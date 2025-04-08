"""Simple example script showing basic usage of kybra_simple_db with:

- Creation modification and deletion of objects.
- Properties and relationships."""

from kybra_simple_logging import get_logger

from kybra_simple_db import (
    Database,
    Entity,
    Integer,
    ManyToMany,
    ManyToOne,
    OneToMany,
    OneToOne,
    String,
)

logger = get_logger(__name__)


def run():
    class Person(Entity):
        name = String(min_length=2, max_length=50)
        age = Integer(min_value=0, max_value=150)
        friends = ManyToMany("Person", "friends")
        mother = ManyToOne("Person", "children")
        children = OneToMany("Person", "mother")
        spouse = OneToOne("Person", "spouse")

    # Create and save a person
    john = Person(name="John", age=30)

    # Update the person's age
    john.age = 33  # Type checking and validation happens automatically

    # _id can be used to load an entity
    Person(_id="peter", name="Peter")
    peter = Person["peter"]

    # Delete the person
    peter.delete()
    assert Person.load("peter") is None

    alice = Person(name="Alice")
    eva = Person(name="Eva")

    john.mother = alice

    eva.friends = [alice]

    # Get storage contents
    Database.get_instance().dump_json(pretty=True)

    return 0


if __name__ == "__main__":
    exit(run())
