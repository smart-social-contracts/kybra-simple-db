# Kybra Simple DB

A lightweight key-value database with entity relationships and audit logging capabilities, intended for small to medium-sized applications running on the Internet Computer using Kybra.

[![Test on IC](https://github.com/smart-social-contracts/kybra-simple-db/actions/workflows/test_ic.yml/badge.svg)](https://github.com/smart-social-contracts/kybra-simple-db/actions)
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

Your canister's storage must be initialized before using Kybra Simple DB. Here's an example of how to do it:

```python
from kybra import StableBTreeMap
from kybra_simple_db import Database

# Initialize storage and database
storage = StableBTreeMap[str, str](memory_id=1, max_key_size=100, max_value_size=1000)
db = Database(storage, audit_enabled=True)
```

then define your entities:

```python
from kybra_simple_db import (
    Entity, String, Integer, Float, Boolean,
    OneToOne, OneToMany, ManyToOne, ManyToMany, TimestampedMixin
)

# Define your entities with relationships
class User(Entity, TimestampedMixin):
    age = Integer(min_value=13, max_value=120)
    posts = OneToMany("Post", "author")
    profile = OneToOne("Profile", "user")
    liked_posts = ManyToMany("Post", "liked_by")


class Profile(Entity):
    bio = String(max_length=500)
    website = String()
    user = OneToOne("User", "profile")

class Post(Entity, TimestampedMixin):
    title = String(min_length=3, max_length=100)
    content = String(min_length=10)
    is_published = Boolean(default=False)
    view_count = Integer(default=0)
    author = ManyToOne("User", "posts")
    liked_by = ManyToMany("User", "liked_posts")
    tags = ManyToMany("Tag", "posts")

class Tag(Entity):
    name = String(min_length=1, max_length=30)
    posts = ManyToMany("Post", "tags")
```

This is an example showcasing the use of the library:

```
# Create users
alice = User(name="Alice Smith", email="alice@example.com", age=28)
bob = User(name="Bob Jones", email="bob@example.com", age=34)

# Create profile with one-to-one relationship
alice_profile = Profile(bio="Software engineer and blogger", website="https://alice.dev")
alice.profile = alice_profile

# Create posts with author relationship
tech_post = Post(
    title="Understanding the IC",
    content="The Internet Computer is a blockchain that provides...",
    author=alice
)
travel_post = Post(
    title="My Trip to Japan",
    content="Last month, I visited Tokyo and Kyoto...",
    author=alice
)

# Create and assign tags (many-to-many)
tech_tag = Tag(name="Technology")
travel_tag = Tag(name="Travel")
japan_tag = Tag(name="Japan")

tech_post.tags = [tech_tag]
travel_post.tags = [travel_tag, japan_tag]

# Many-to-many relationship (likes)
bob.liked_posts = [tech_post]

# Retrieve entities by ID
retrieved_user = User[alice.id()]
assert retrieved_user.name == "Alice Smith"

# Query by relationships
alice_posts = alice.posts                  # All posts by Alice
assert len(alice_posts) == 2

japan_posts = japan_tag.posts              # All posts with Japan tag
assert japan_posts[0].title == "My Trip to Japan"

tech_post_likers = tech_post.liked_by      # Users who liked tech post
assert bob in tech_post_likers

# Update entities
travel_post.view_count = 42
travel_post.is_published = True

# Access audit trail and timestamps
print(f"Alice was created at: {alice._timestamp_created}")
print(f"Profile owner: {alice_profile._owner}")
print(f"Last updated by: {travel_post._updater}")

# Delete entities (with relationship cleanup)
bob.delete()  # Also removes bob from tech_post.liked_by

# Database operations
all_data = db.get_all()                    # Get all stored entities
json_export = db.dump_json(pretty=True)    # Export database as JSON
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
