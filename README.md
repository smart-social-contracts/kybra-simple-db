# Kybra Simple DB

A lightweight key-value database with entity relationships and audit logging capabilities, intended for small to medium-sized applications running on the Internet Computer using Kybra.

[![Test](https://github.com/smart-social-contracts/kybra-simple-db/actions/workflows/test.yml/badge.svg)](https://github.com/smart-social-contracts/kybra-simple-db/actions)
[![PyPI version](https://badge.fury.io/py/kybra-simple-db.svg)](https://badge.fury.io/py/kybra-simple-db)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3107/)
[![Coverage](https://codecov.io/gh/smart-social-contracts/kybra-simple-db/branch/main/graph/badge.svg)](https://codecov.io/gh/smart-social-contracts/kybra-simple-db)
[![License](https://img.shields.io/github/license/smart-social-contracts/kybra-simple-db.svg)](https://github.com/smart-social-contracts/kybra-simple-db/blob/main/LICENSE)

## Features

- **Entity-Relational Database**: Create and manage entities with complex relationships
- **Type System**: Define properties with proper typing (String, Integer, Float, Boolean)
- **Relationship Types**: Support for OneToOne, OneToMany, ManyToOne, and ManyToMany relationships
- **Audit Logging**: Track all changes to your data with built-in audit trails
- **Timestamped Entities**: Add created/updated timestamps to entities with mixins
- **Flexible Storage**: Works with Kybra's StableBTreeMap for persistent storage on the Internet Computer

## Installation

```bash
pip install kybra-simple-db
```

## Quick Start

### Basic Setup

```python
# Step 1: Import Kybra and define storage
from kybra import StableBTreeMap

# Create a StableBTreeMap for database storage
db_storage = StableBTreeMap[str, str](
    memory_id=1,  # Unique memory ID for this map
    max_key_size=100,  # Maximum key size in bytes
    max_value_size=1000  # Maximum value size in bytes
)

# Step 2: Import Kybra Simple DB and initialize database
from kybra_simple_db import Database, Entity, String, Integer

# Initialize the database with your storage
db = Database(db_storage, audit_enabled=True)
```

### Creating and Using Entities

```python
# Define a User entity
class User(Entity):
    def __init__(self, username, email, age):
        super().__init__(entity_type="user")
        self.username = String(username)
        self.email = String(email)
        self.age = Integer(age)

# Create and save a user
user = User("johndoe", "john@example.com", 30)
user.save()

# Retrieve a user by ID
user_id = user.id()  # Get the user's ID
retrieved_user = Entity.get(User, user_id)  # Retrieve by ID

# Update a user property
retrieved_user.update("age", 31)

# Delete a user
retrieved_user.delete()
```

### Working with Relationships

```python
# Define entities with relationships
class Post(Entity):
    def __init__(self, title, content, author):
        super().__init__(entity_type="post")
        self.title = String(title)
        self.content = String(content)
        # Create relationship to author (User)
        self.add_relation("author", "posts", author)

# Create related entities
user = User("johndoe", "john@example.com", 30)
user.save()

post = Post("First Post", "Hello World!", user)
post.save()

# Access relationships
post_author = post.get_relations(User, "author")[0]  # Get the post's author
user_posts = user.get_relations(Post, "posts")  # Get all posts by the user
```

## API Reference

### Core Classes

- `Database`: Main database engine for storage operations
- `Entity`: Base class for all database entities
- `Storage` / `MemoryStorage`: Storage interfaces for data persistence

### Property Types

- `String`: String property type
- `Integer`: Integer property type
- `Float`: Float property type
- `Boolean`: Boolean property type

### Relationship Types

- `OneToOne`: One-to-one relationship between entities
- `OneToMany`: One-to-many relationship between entities
- `ManyToOne`: Many-to-one relationship between entities
- `ManyToMany`: Many-to-many relationship between entities

### Mixins

- `TimestampedMixin`: Adds created_at and updated_at fields to entities

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/smart-social-contracts/kybra-simple-db.git
cd kybra-simple-db

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
```

### Run Tests

```bash
pytest tests/
```

### Run Linters

```bash
./run_linters.sh
```

## Versioning

This project uses [bumpversion](https://pypi.org/project/bumpversion/) for version management. To increment the version:

```bash
# For patch version (0.1.2 -> 0.1.3)
bumpversion patch

# For minor version (0.1.2 -> 0.2.0)
bumpversion minor

# For major version (0.1.2 -> 1.0.0)
bumpversion major
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

