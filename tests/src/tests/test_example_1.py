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


def run(test_name: str = None, test_var: str = None):
    class Person(Entity):
        name = String(min_length=2, max_length=50)
        age = Integer(min_value=0, max_value=150)
        friends = ManyToMany("Person", "friends")
        mother = ManyToOne("Person", "children")
        children = OneToMany("Person", "mother")
        spouse = OneToOne("Person", "spouse")

    # Create and save a person
    john = Person(name="John", age=30)
    assert john.name == "John"
    assert john.age == 30

    # Update the person's age
    john.age = 33  # Type checking and validation happens automatically
    assert john.age == 33

    # _id can be used to load an entity
    Person(_id="peter", name="Peter")
    peter = Person["peter"]
    assert peter.name == "Peter"

    # Delete the person
    peter.delete()
    assert Person.load("peter") is None

    alice = Person(name="Alice")
    eva = Person(name="Eva")

    john.mother = alice
    assert john.mother == alice
    # Check reverse relationship - alice should have john as a child
    assert john in alice.children

    eva.friends = [alice]
    assert alice in eva.friends
    assert eva in alice.friends

    # Get storage contents
    dump = Database.get_instance().dump_json(pretty=True)
    assert dump is not None
    # Verify that the dump contains our entities
    assert "Person" in dump

    return 0


if __name__ == "__main__":
    Database.get_instance().clear()
    exit(run())
