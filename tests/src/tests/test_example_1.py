"""Simple example script showing basic usage of kybra_simple_db with properties."""

import kybra_simple_db as ksdb


def run():
    log = ksdb.get_logger()

    class Person(ksdb.Entity):
        name = ksdb.String(min_length=2, max_length=50)
        age = ksdb.Integer(min_value=0, max_value=150)
        friends = ksdb.ManyToMany("Person", "friends")
        mother = ksdb.ManyToOne("Person", "children")
        children = ksdb.OneToMany("Person", "mother")
        spouse = ksdb.OneToOne("Person", "spouse")

    # Create and save a person
    person = Person(name="John", age=30)
    log("Created person: %s" % {"name": person.name, "age": person.age})

    # Load the person - use the cached instance since we just saved it
    log("Loaded person:%s" % {"name": person.name, "age": person.age})

    # Update the person's age
    person.age = 31  # Type checking and validation happens automatically
    log("Updated person:%s" % {"name": person.name, "age": person.age})

    # _id can be used to load an entity
    _ = Person(_id="peter", name="Peter")
    peter_loaded = Person["peter"]
    log(peter_loaded.to_dict())

    # [] operator can be used to load an entity
    peter_loaded_2 = Person["peter"]
    log(peter_loaded_2.to_dict())

    # Print storage contents
    log("\nStorage contents:")
    log(ksdb.Database.get_instance().raw_dump_json(pretty=True))

    # Delete the person
    person.delete()
    deleted = Person.load("1")
    log("After delete:%s" % deleted)  # None


    alice = Person(name="Alice")
    laura = Person(name="Laura")
    eva = Person(name="Eva")

    alice.mother = eva
    laura.mother = eva

    laura.friends = [alice, eva]
    eva.friends = [laura, alice]


    alice.spouse = laura

    print([c.name for c in eva.children])
    print([c.name for c in eva.friends])
    print(alice.mother.name)
    print([c.name for c in alice.friends])
    print(laura.spouse.name)


    return 0


if __name__ == "__main__":
    exit(run())
