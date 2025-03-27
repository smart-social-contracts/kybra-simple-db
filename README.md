# Kybra Simple DB


# TODO:
test canister update persistance of db data and instantiation
add support for default values of properties


review audit and test examples
add coverage
linting
final cleaning
    readme
    remove printouts, TODO, etc.
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

# Step 1: Import Kybra and define storage
from kybra import StableBTreeMap
db_storage  = StableBTreeMap[str, str](memory_id=..., max_key_size=..., max_value_size=...)

# Step 2: Import Kybra Simple DB and initialize database
from kybra_simple_db import *
Database(db_storage)

# Step 3: Run your application using the database

# TODO
```

### Installation

On your Kybra project, copy the folder

TODO: insert directory tree

If not using Kybra, just:
```
pip install ...
```

## Features

- Uses IC persistent storage (StableBTreeMap)when used on the Internet Computer, although it can be run outside IC using a custom storage object.
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


### Advance usage

[Example 2](./tests/src/tests/test_2.py)

```python
TODO
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

MIT