# Access Control with Context Management

This guide shows how to implement access control using the `on_event` hooks combined with the `as_user()` context manager.

## Overview

The `kybra-simple-db` provides thread-safe context management for tracking the current user:

- **`db.as_user(user_id)`** - Context manager for running operations as a specific user
- **`get_caller_id()`** - Get the current user ID
- **`set_caller_id(user_id)`** - Set the current user ID

## Basic Usage

```python
from kybra_simple_db import Database, Entity, String
from kybra_simple_db.mixins import TimestampedMixin

db = Database.get_instance()

class Document(Entity, TimestampedMixin):
    title = String()

# Create documents as different users
with db.as_user("alice"):
    doc1 = Document(title="Alice's Doc")  # Owner: alice

with db.as_user("bob"):
    doc2 = Document(title="Bob's Doc")  # Owner: bob
```

## Access Control Pattern

Combine `as_user()` with `on_event` hooks for access control:

```python
from kybra_simple_db import ACTION_MODIFY, ACTION_DELETE, Entity, String
from kybra_simple_db.context import get_caller_id
from kybra_simple_db.mixins import TimestampedMixin

class ProtectedDocument(Entity, TimestampedMixin):
    title = String()
    content = String()

    @staticmethod
    def on_event(entity, field_name, old_value, new_value, action):
        caller_id = get_caller_id()

        # Only owner can modify or delete
        if action in (ACTION_MODIFY, ACTION_DELETE):
            if entity._owner != caller_id:
                return False, None  # Deny access

        return True, new_value
```

## Nested Contexts

Contexts can be nested and automatically reset:

```python
with db.as_user("admin"):
    admin_doc = Document(title="Admin Doc")  # Owner: admin
    
    with db.as_user("user"):
        user_doc = Document(title="User Doc")  # Owner: user
    
    # Back to admin context
    another_doc = Document(title="Another Admin")  # Owner: admin
```

## Benefits

### Thread-Safe
Uses Python's `contextvars` for proper thread/async isolation:

```python
# Different threads won't interfere with each other
import threading

def create_doc(user_id):
    with db.as_user(user_id):
        doc = Document(title=f"Doc for {user_id}")
        print(f"Created by: {doc._owner}")

t1 = threading.Thread(target=create_doc, args=("alice",))
t2 = threading.Thread(target=create_doc, args=("bob",))
t1.start()
t2.start()
```

### Automatic Cleanup
Context manager ensures caller ID is reset even if exceptions occur:

```python
try:
    with db.as_user("alice"):
        doc = Document(title="Test")
        raise RuntimeError("Error!")
except RuntimeError:
    pass

# Caller is automatically reset to previous value
print(get_caller_id())  # 'system'
```

### Clear Scope
Easy to see which operations run as which user:

```python
# Everything in this block runs as alice
with db.as_user("alice"):
    doc = Document(title="Doc 1")
    doc.content = "Updated"
    doc.save()
```

## Advanced Patterns

### Admin Override

```python
class ProtectedEntity(Entity, TimestampedMixin):
    value = String()
    
    ADMINS = ["admin", "superuser"]
    
    @staticmethod
    def on_event(entity, field_name, old_value, new_value, action):
        caller = get_caller_id()
        
        # Admins can do anything
        if caller in ProtectedEntity.ADMINS:
            return True, new_value
        
        # Others need ownership
        if action in (ACTION_MODIFY, ACTION_DELETE):
            if entity._owner != caller:
                return False, None
        
        return True, new_value
```

### Field-Level Access

```python
class Employee(Entity, TimestampedMixin):
    name = String()
    salary = Integer()
    
    @staticmethod
    def on_event(entity, field_name, old_value, new_value, action):
        caller = get_caller_id()
        
        # Salary requires HR permission
        if field_name == "salary" and action == ACTION_MODIFY:
            if caller not in ["hr_manager", "admin"]:
                return False, None
        
        return True, new_value
```

### Audit Trail

```python
class AuditedEntity(Entity, TimestampedMixin):
    value = String()
    
    audit_log = []
    
    @staticmethod
    def on_event(entity, field_name, old_value, new_value, action):
        caller = get_caller_id()
        
        # Log all access attempts
        AuditedEntity.audit_log.append({
            "caller": caller,
            "action": action,
            "field": field_name,
            "old": old_value,
            "new": new_value
        })
        
        return True, new_value
```

## Migration from os.environ

If you were using `os.environ.get("CALLER_ID")`, migrate to the new context approach:

### Before (Not Thread-Safe)
```python
import os

os.environ["CALLER_ID"] = "alice"
doc = Document(title="My Doc")
os.environ["CALLER_ID"] = "system"  # Easy to forget!
```

### After (Thread-Safe)
```python
with db.as_user("alice"):
    doc = Document(title="My Doc")
# Automatically resets
```

## See Also

- [HOOKS.md](HOOKS.md) - Complete hooks documentation
- [examples/simple_access_control.py](../examples/simple_access_control.py) - Working example
