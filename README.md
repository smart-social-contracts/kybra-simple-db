# Kybra Simple DB


# TODO:
review audit and test examples
add coverage
linting
final cleaning
    readme
    printouts, TODO, etc.
RELEASE!

[![Test](https://github.com/Batou125/kybra_simple_db/actions/workflows/test.yml/badge.svg)](https://github.com/Batou125/kybra_simple_db/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/kybra-simple-db.svg)](https://badge.fury.io/py/kybra-simple-db)
[![Python Versions](https://img.shields.io/pypi/pyversions/kybra-simple-db.svg)](https://pypi.org/project/kybra-simple-db/)
[![Coverage](https://codecov.io/gh/Batou125/kybra_simple_db/branch/main/graph/badge.svg)](https://codecov.io/gh/Batou125/kybra_simple_db)
[![License](https://img.shields.io/github/license/Batou125/kybra_simple_db.svg)](https://github.com/Batou125/kybra_simple_db/blob/main/LICENSE)

A lightweight key-value database with entity relationships and audit logging capabilities, intended for small to medium-sized applications running on the Internet Computer using Kybra.

## Quick Start

### Basic Usage

[Example 1](./tests/src/tests/test_1.py)

```python
from kybra_simple_db import *

TODO
```

### Installation

On your Kybra project, copy the folder

TODO: insert directory tree

If not using Kybra, just:
```
pip install ...
```

## Features

- Uses IC persistent storage when used on the Internet Computer, although it can be run outside IC using a custom storage object.
- No need for calling ".save()". Just use the variables seamlessly (TODO: explain better)
- Simple key-value storage with JSON serialization
- Entity-relationship management
- Audit logging of all operations
- Pluggable storage backends
- Type hints for better IDE support
- Zero dependencies
- Python 3.10.7 support
- Timestamp and ownership tracking via mixins
- System time management for testing and synchronization


### Using Entities and Relationships

[Example 2](./tests/src/tests/test_2.py)

```python
from kybra_simple_db import *

class User(Entity, TimestampedMixin):
    pass

class Department(Entity):
    pass

user = User("user", name="John", age=30)  # Automatically sets creation timestamp and owner
dept = Department("department", name="IT")

# View timestamps and ownership
print(user.to_dict())
# {
#   "name": "John",
#   "age": 30,
#   "timestamp_created": "2025-02-09 15:32:46 (1739111966)",
#   "timestamp_updated": "2025-02-09 15:32:46 (1739111966)",
#   "creator": "system",
#   "updater": "system",
#   "owner": "system"
# }
```

### Entity Inheritance

[Example 3](./tests/src/tests/test_3.py)

The database supports inheritance between entity classes. This allows you to create a hierarchy of entities and query instances based on their type:

```python
from kybra_simple_db import *

# Define base class
class Animal(Entity, TimestampedMixin):
    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name

# Define subclasses
class Dog(Animal):
    pass

class Cat(Animal):
    pass

# Create instances
animal_a = Animal(name='Alice')
dog_b = Dog(name='Bob')
cat_c = Cat(name='Charlie')

# Save instances
for entity in [animal_a, dog_b, cat_c]:
    entity.save()

# Query instances by type
all_animals = Animal.instances()  # Returns [animal_a, dog_b, cat_c]
dogs = Dog.instances()           # Returns [dog_b]
cats = Cat.instances()           # Returns [cat_c]
```

The `instances()` class method supports inheritance:
- When called on a base class (e.g., `Animal`), it returns instances of that class and all its subclasses
- When called on a subclass (e.g., `Dog`), it returns only instances of that specific class

### Audit Logging

[Example 4](./tests/src/tests/test_4.py)

```python
from kybra_simple_db import *

# Create database with audit logging
db = Database(MemoryStorage(), MemoryStorage())

# Perform operations
db.save("user1", {"name": "John"})

# View audit log
print(db.get_audit())
```


### Running Tests

To run the test suite:

```bash
pip install -r requirements-dev.txt
python -m pytest -v
python -m pylint kybra_simple_db tests
```


## Development

```bash
# Clone the repository
git clone https://github.com/smart-social-contracts/kybra_simple_db.git
cd kybra_simple_db

# Recommended steps
pip install pyenv virtualenv
pyenv local 3.10.7
python -m virtualenv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
cd tests && ./run_test.sh

# Run linters
black .
isort .
flake8 .
mypy .
```

## License

MIT License