# Kybra Simple DB

A lightweight key-value database with entity relationships and audit logging capabilities, intended for small to medium-sized applications running on the Internet Computer using Kybra.

[![Test](https://github.com/smart-social-contracts/kybra-simple-db/actions/workflows/test.yml/badge.svg)](https://github.com/smart-social-contracts/kybra-simple-db/actions)
[![PyPI version](https://badge.fury.io/py/kybra-simple-db.svg)](https://badge.fury.io/py/kybra-simple-db)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3107/)
[![Coverage](https://codecov.io/gh/smart-social-contracts/kybra-simple-db/branch/main/graph/badge.svg)](https://codecov.io/gh/smart-social-contracts/kybra-simple-db)
[![License](https://img.shields.io/github/license/smart-social-contracts/kybra-simple-db.svg)](https://github.com/smart-social-contracts/kybra-simple-db/blob/main/LICENSE)

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
```
