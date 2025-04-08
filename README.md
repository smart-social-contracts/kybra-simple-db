# Kybra Simple DB

A lightweight key-value database with entity relationships and audit logging capabilities, intended for small to medium-sized applications running on the Internet Computer using Kybra.

[![Test on IC](https://github.com/smart-social-contracts/kybra-simple-db/actions/workflows/test_ic.yml/badge.svg)](https://github.com/smart-social-contracts/kybra-simple-db/actions)
[![Test](https://github.com/smart-social-contracts/kybra-simple-db/actions/workflows/test.yml/badge.svg)](https://github.com/smart-social-contracts/kybra-simple-db/actions)
[![PyPI version](https://badge.fury.io/py/kybra-simple-db.svg)](https://badge.fury.io/py/kybra-simple-db)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3107/)
[![License](https://img.shields.io/github/license/smart-social-contracts/kybra-simple-db.svg)](https://github.com/smart-social-contracts/kybra-simple-db/blob/main/LICENSE)

## Features

- **Persistent Storage**: Works with Kybra's StableBTreeMap stable structure for persistent storage on your canister's stable memory so your data persists automatically across canister upgrades.
- **Entity-Relational Database**: Create, read and write entities with OneToOne, OneToMany, ManyToOne, and ManyToMany relationships.
- **Audit Logging**: Track all changes to your data with created/updated timestamps and who created and updated each entity.
- **Ownership**: Assign owners to your data objects to control who can modify them.


## Installation

```bash
pip install kybra-simple-db
```

## Quick Start

The database storage must be initialized before using Kybra Simple DB. Here's an example of how to do it:

```python
from kybra import StableBTreeMap
from kybra_simple_db import Database

# Initialize storage and database
storage = StableBTreeMap[str, str](memory_id=1, max_key_size=100, max_value_size=1000)  # Use a unique memory ID for each storage instance
Database(storage, audit_enabled=True)
```

Read [Kybra's documentation](https://demergent-labs.github.io/kybra/stable_structures.html?highlight=StableBTreeMap) for more information regarding StableBTreeMap and memory IDs.

Next, define your entities:

```python
from kybra_simple_db import (
    Database, Entity, String, Integer,
    OneToOne, OneToMany, ManyToOne, ManyToMany, TimestampedMixin
)

class Person(Entity, TimestampedMixin):
    name = String(min_length=2, max_length=50)
    age = Integer(min_value=0, max_value=120)
    friends = ManyToMany("Person", "friends")
    mother = ManyToOne("Person", "children")
    children = OneToMany("Person", "mother")
    spouse = OneToOne("Person", "spouse")
```

Then use the defined entities to store objects:

```python
    # Create and save an object
    john = Person(name="John", age=30)

    # Update an object's property
    john.age = 33  # Type checking and validation happens automatically

    # use the `_id` property to load an entity with the [] operator
    Person(_id="peter", name="Peter")
    peter = Person["peter"]

    # Delete an object
    peter.delete()

    # Create relationships
    alice = Person(name="Alice")
    eva = Person(name="Eva")
    john.mother = alice
    assert john in alice.children
    eva.friends = [alice]
    assert alice in eva.friends
    assert eva in alice.friends

    pprint(alice.to_dict())  # Prints the dictionary representation of an object
    ''' Prints:

    {'_id': '2',
    '_type': 'Person',
    'age': None,
    'creator': 'system',
    'name': 'Alice',
    'owner': 'system',
    'relations': {'children': [{'_id': '1', '_type': 'Person'}],
                'friends': [{'_id': '3', '_type': 'Person'}]},
    'timestamp_created': '2025-04-08 20:45:08.957',
    'timestamp_updated': '2025-04-08 20:45:08.957',
    'updater': 'system'}

    '''

    # Retrieve database contents in JSON format
    print(Database.get_instance().dump_json(pretty=True))

    # Audit log
    audit_records = Database.get_instance().get_audit(id_from=0, id_to=5)
    pprint(audit_records['0'])
    ''' Prints:

    ['save',
    1744138342934,
    'Person@1',
    {'_id': '1',
    '_type': 'Person',
    'age': 30,
    'creator': 'system',
    'name': 'John',
    'owner': 'system',
    'timestamp_created': '2025-04-08 20:52:22.934',
    'timestamp_updated': '2025-04-08 20:52:22.934',
    'updater': 'system'}]

    '''
```

## API Reference

- **Core**: `Database`, `Entity`
- **Properties**: `String`, `Integer`, `Float`, `Boolean`
- **Relationships**: `OneToOne`, `OneToMany`, `ManyToOne`, `ManyToMany`
- **Mixins**: `TimestampedMixin` (timestamps and ownership tracking)

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/smart-social-contracts/kybra-simple-db.git
cd kybra-simple-db

# Recommended setup
pyenv install 3.10.7
pyenv local 3.10.7
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Running tests
./run_linters.sh && (cd tests && ./run_test.sh && ./run_test_ic.sh)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT](LICENSE).
