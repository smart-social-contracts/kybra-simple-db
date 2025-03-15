import logging

from kybra_simple_db import *

# Configure logging - only show INFO and above
logging.basicConfig(level=logging.INFO)

# Set up database
db = Database(MemoryStorage())
Database._instance = db


class Person(Entity):
    name = String(min_length=2, max_length=50)
    friends = ManyToMany("Person", "friends")
    mother = ManyToOne("Person", "children")
    children = OneToMany("Person", "mother")
    spouse = OneToOne("Person", "spouse")


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
