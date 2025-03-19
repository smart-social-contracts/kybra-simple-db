"""Simple example script showing basic usage of kybra_simple_db with:

- Creation modification and deletion of objects.
- Properties and relationships."""

from kybra_simple_db import Entity, String, Integer, ManyToMany, ManyToOne, OneToMany, OneToOne, Database, get_logger


def run():
    log = get_logger()

    class Person(Entity):
        name = String(min_length=2, max_length=50)
        age = Integer(min_value=0, max_value=150)
        friends = ManyToMany("Person", "friends")
        mother = ManyToOne("Person", "children")
        children = OneToMany("Person", "mother")
        spouse = OneToOne("Person", "spouse")

    # Create and save a person
    john = Person(name="John", age=30)
    log("Created person: %s" % {"name": john.name, "age": john.age})

    # Update the person's age
    john.age = 33 # Type checking and validation happens automatically
    log("\nUpdated person:%s" % {"name": john.name, "age": john.age})

    # _id can be used to load an entity
    Person(_id="peter", name="Peter")
    peter = Person["peter"]
    log("\nPeter loaded: %s" % peter.to_dict())  # convert to dict

    # Delete the person
    log("1")
    peter.delete()
    log("2")
    deleted = Person.load("peter")
    log("\nPeter after deleation: %s" % deleted)  # shows None

    alice = Person(name="Alice")
    eva = Person(name="Eva")
    
    john.mother = alice

    eva.friends = [alice]

    # Print storage contents
    log("\nStorage contents:")
    log(Database.get_instance().dump_json(pretty=True))

    return 0


if __name__ == "__main__":
    exit(run())
