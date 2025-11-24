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
- **Entity Hooks**: Intercept and control entity lifecycle events (create, modify, delete) with `on_event` hooks.
- **Access Control**: Thread-safe context management for user identity tracking and ownership-based permissions.
- **Namespaces**: Organize entities into namespaces to avoid type conflicts when you have multiple entities with the same class name.
- **Audit Logging**: Track all changes to your data with created/updated timestamps and who created and updated each entity.


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

Organize entities with the `__namespace__` attribute to avoid type conflicts when you have the same class name in different modules:

```python
# In app/models.py
class User(Entity):
    __namespace__ = "app"
    name = String()
    role = String()
```

```python
# In admin/models.py  
class User(Entity):
    __namespace__ = "admin"
    name = String()
    permissions = String()
```

```python
from app.models import User as AppUser
from admin.models import User as AdminUser

app_user = AppUser(name="Alice", role="developer")      # Stored as "app::User"
admin_user = AdminUser(name="Bob", permissions="all")     # Stored as "admin::User"

# Each namespace has isolated ID sequences and storage
assert app_user._id == "1"
assert admin_user._id == "1"
```

## Entity Hooks

Intercept and control entity changes with the `on_event` hook:

```python
from kybra_simple_db import Entity, String, ACTION_MODIFY

class User(Entity):
    name = String()
    email = String()
    
    @staticmethod
    def on_event(entity, field_name, old_value, new_value, action):
        # Validate email format
        if field_name == "email" and "@" not in new_value:
            return False, None  # Reject invalid email
        
        # Auto-capitalize names
        if field_name == "name":
            return True, new_value.upper()
        
        return True, new_value

user = User(name="alice", email="alice@example.com")
assert user.name == "ALICE"  # Auto-capitalized
```

See [docs/HOOKS.md](docs/HOOKS.md) for more patterns.

## Access Control

Thread-safe user context management with `as_user()`:

```python
from kybra_simple_db import Database, Entity, String, ACTION_MODIFY, ACTION_DELETE
from kybra_simple_db.mixins import TimestampedMixin
from kybra_simple_db.context import get_caller_id

class Document(Entity, TimestampedMixin):
    title = String()
    
    @staticmethod
    def on_event(entity, field_name, old_value, new_value, action):
        caller = get_caller_id()
        
        # Only owner can modify or delete
        if action in (ACTION_MODIFY, ACTION_DELETE):
            if entity._owner != caller:
                return False, None
        
        return True, new_value

db = Database.get_instance()

# Alice creates a document
with db.as_user("alice"):
    doc = Document(title="My Doc")  # Owner: alice

# Bob cannot modify Alice's document
with db.as_user("bob"):
    doc.title = "Hacked"  # Raises ValueError
```

See [docs/ACCESS_CONTROL.md](docs/ACCESS_CONTROL.md) and [examples/simple_access_control.py](examples/simple_access_control.py).

## API Reference

- **Core**: `Database`, `Entity`
- **Properties**: `String`, `Integer`, `Float`, `Boolean`
- **Relationships**: `OneToOne`, `OneToMany`, `ManyToOne`, `ManyToMany`
- **Mixins**: `TimestampedMixin` (timestamps and ownership tracking)
- **Hooks**: `ACTION_CREATE`, `ACTION_MODIFY`, `ACTION_DELETE`
- **Context**: `get_caller_id()`, `set_caller_id()`, `Database.as_user()`

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
