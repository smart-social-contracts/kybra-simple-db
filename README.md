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
- **Namespaces**: Organize entities into namespaces to avoid type conflicts when you have multiple entities with the same class name.
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
Database.init(db_storage=storage)
```

Read [Kybra's documentation](https://demergent-labs.github.io/kybra/stable_structures.html?highlight=StableBTreeMap) for more information regarding StableBTreeMap and memory IDs.

Next, define your entities:

```python
from kybra_simple_db import (
    Database, Entity, String, Integer,
    OneToOne, OneToMany, ManyToOne, ManyToMany, TimestampedMixin
)

class Person(Entity, TimestampedMixin):
    __alias__ = "name"  # Use `name` as the alias field for lookup by `name`
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
    Person(name="Peter")
    peter = Person["Peter"]

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

    print(alice.serialize())  # Prints the dictionary representation of an object
    # Prints: {'timestamp_created': '2025-09-12 22:15:35.882', 'timestamp_updated': '2025-09-12 22:15:35.883', 'creator': 'system', 'updater': 'system', 'owner': 'system', '_type': 'Person', '_id': '3', 'name': 'Alice', 'age': None, 'children': '1', 'friends': '4'}

    assert Person.count() == 3
    assert Person.max_id() == 4
    assert Person.instances() == [john, alice, eva]

    # Cursor-based pagination
    assert Person.load_some(0, 2) == [john, alice]
    assert Person.load_some(2, 2) == [eva]

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

For more usage examples, see the [tests](tests/src/tests).

## Namespaces

Namespaces allow you to organize entities and avoid type name conflicts when you have multiple entities with the same class name. This is particularly useful when working with different domains or modules that may have similar entity types.

### Usage

Define a namespace by setting the `__namespace__` class attribute:

```python
from kybra_simple_db import Entity, String

# Regular entity without namespace
class User(Entity):
    name = String()
    email = String()

# Entity in the "app" namespace
class AppUser(Entity):
    __namespace__ = "app"
    name = String()
    email = String()
    role = String()

# Entity in the "admin" namespace
class AdminUser(Entity):
    __namespace__ = "admin"
    name = String()
    email = String()
    permissions = String()
```

### Key Features

- **Isolated Storage**: Each namespace maintains its own ID sequence and storage space
- **Type Separation**: Entities are stored with their namespace prefix (e.g., `"app::AppUser"`, `"admin::AdminUser"`)
- **Independent Operations**: `count()`, `instances()`, and other class methods operate within the namespace
- **Alias Support**: Aliases work correctly within namespaces

### Example

```python
# Create entities in different namespaces
regular_user = User(name="John", email="john@example.com")
app_user = AppUser(name="Alice", email="alice@app.com", role="developer")
admin_user = AdminUser(name="Bob", email="bob@admin.com", permissions="all")

# Each starts with ID "1" in their own namespace
assert regular_user._id == "1"  # User@1
assert app_user._id == "1"       # app::AppUser@1
assert admin_user._id == "1"     # admin::AdminUser@1

# Verify type names include namespace
assert regular_user._type == "User"
assert app_user._type == "app::AppUser"
assert admin_user._type == "admin::AdminUser"

# Operations are namespace-isolated
assert User.count() == 1
assert AppUser.count() == 1
assert AdminUser.count() == 1

# Load entities independently
loaded_app = AppUser.load("1")
loaded_admin = AdminUser.load("1")
assert loaded_app.name == "Alice"
assert loaded_admin.name == "Bob"
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
