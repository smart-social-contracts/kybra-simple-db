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


def run(test_name: str = None, test_var: str = None):
    assert len(Person.instances()) == 1

    bob = Person(name="Bob")
    assert bob.name == "Bob"

    assert len(Person.instances()) == 2

    assert Person["1"].name == "Alice"
    assert Person["2"].name == "Bob"

    return 0


if __name__ == "__main__":
    Database.get_instance().clear()
    exit(run())
