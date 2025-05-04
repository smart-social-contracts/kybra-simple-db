"""Simple example script showing basic usage of kybra_simple_db with:

- Creation modification and deletion of objects.
- Properties and relationships."""

from kybra_simple_logging import get_logger

from kybra_simple_db import (
    Database,
    Entity,
    String,
)

logger = get_logger(__name__)


class Person(Entity):
    name = String(min_length=2, max_length=50)


def run():
    # Create and save a person
    alice = Person(name="Alice")
    assert alice.name == "Alice"

    assert len(Person.instances()) == 1
    assert Person["1"].name == "Alice"

    return 0


if __name__ == "__main__":
    Database.get_instance().clear()
    exit(run())
