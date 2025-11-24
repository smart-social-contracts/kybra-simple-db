"""Tests for entity on_event hook system."""

import pytest
from kybra_simple_db import (
    Database, Entity, String, Integer,
    ACTION_CREATE, ACTION_MODIFY, ACTION_DELETE
)


@pytest.fixture(autouse=True)
def setup():
    Database.get_instance().clear()
    yield
    Database.get_instance().clear()


def test_reject_invalid_value():
    """Hook can reject invalid values."""
    
    class User(Entity):
        age = Integer()
        
        @staticmethod
        def on_event(entity, field_name, old_value, new_value, action):
            if field_name == 'age' and new_value is not None and new_value < 0:
                return False, None
            return True, new_value
    
    user = User(age=25)
    assert user.age == 25
    
    with pytest.raises(ValueError, match="Hook rejected"):
        user.age = -5


def test_transform_value():
    """Hook can transform values."""
    
    class User(Entity):
        name = String()
        age = Integer()
        
        @staticmethod
        def on_event(entity, field_name, old_value, new_value, action):
            if field_name == 'name' and new_value:
                return True, new_value.upper()
            if field_name == 'age' and new_value and new_value > 150:
                return True, 150
            return True, new_value
    
    user = User(name='alice', age=200)
    
    assert user.name == 'ALICE'
    assert user.age == 150


def test_prevent_deletion():
    """Hook can prevent entity deletion."""
    
    class User(Entity):
        name = String()
        protected = Integer()
        
        @staticmethod
        def on_event(entity, field_name, old_value, new_value, action):
            if action == ACTION_DELETE and entity.protected == 1:
                return False, None
            return True, new_value
    
    protected = User(name='Admin', protected=1)
    with pytest.raises(PermissionError, match="Hook rejected"):
        protected.delete()
    
    normal = User(name='Guest', protected=0)
    normal.delete()  # Should work


def test_track_changes():
    """Hook can track old and new values."""
    
    changes = []
    
    class User(Entity):
        name = String()
        
        @staticmethod
        def on_event(entity, field_name, old_value, new_value, action):
            if action == ACTION_MODIFY and field_name:
                changes.append({'field': field_name, 'old': old_value, 'new': new_value})
            return True, new_value
    
    user = User(name='Bob')
    changes.clear()
    
    user.name = 'Robert'
    
    assert len(changes) == 1
    assert changes[0] == {'field': 'name', 'old': 'Bob', 'new': 'Robert'}


def test_action_types():
    """Hook receives correct action types."""
    
    actions = []
    
    class User(Entity):
        name = String()
        
        @staticmethod
        def on_event(entity, field_name, old_value, new_value, action):
            actions.append((action, field_name))
            return True, new_value
    
    user = User(name='Test')
    create_actions = [a for a in actions if a[0] == ACTION_CREATE]
    assert len(create_actions) > 0
    
    actions.clear()
    user.name = 'Updated'
    assert (ACTION_MODIFY, 'name') in actions
    
    actions.clear()
    user.delete()
    assert (ACTION_DELETE, None) in actions


def test_no_hook_works_normally():
    """Entities without hooks work normally."""
    
    class User(Entity):
        name = String()
        age = Integer()
    
    user = User(name='Charlie', age=30)
    assert user.name == 'Charlie'
    
    user.age = 35
    assert user.age == 35
    
    user.delete()


def test_hook_bool_return():
    """Hook can return just bool."""
    
    class User(Entity):
        name = String()
        
        @staticmethod
        def on_event(entity, field_name, old_value, new_value, action):
            return True  # Just bool, value unchanged
    
    user = User(name='Test')
    assert user.name == 'Test'


def test_complex_validation():
    """Complex validation scenario."""
    
    class User(Entity):
        username = String()
        email = String()
        age = Integer()
        
        @staticmethod
        def on_event(entity, field_name, old_value, new_value, action):
            if field_name == 'username' and new_value and len(new_value) < 3:
                return False, None
            
            if field_name == 'email' and new_value and '@' not in new_value:
                return False, None
            
            if field_name == 'age' and new_value is not None:
                if new_value < 0 or new_value > 150:
                    return False, None
            
            return True, new_value
    
    # Valid user
    user = User(username='john', email='john@test.com', age=25)
    assert user.username == 'john'
    
    # Invalid username
    with pytest.raises(ValueError):
        user.username = 'ab'
    
    # Invalid email
    with pytest.raises(ValueError):
        user.email = 'invalid'
    
    # Invalid age
    with pytest.raises(ValueError):
        user.age = -5
    
    with pytest.raises(ValueError):
        user.age = 200


def test_auto_generate_field():
    """Hook can auto-generate related fields."""
    
    class User(Entity):
        name = String()
        slug = String()
        
        @staticmethod
        def on_event(entity, field_name, old_value, new_value, action):
            # Auto-generate slug from name
            if field_name == 'name' and new_value and not entity.slug:
                entity._do_not_save = True
                entity.slug = new_value.lower().replace(' ', '-')
                entity._do_not_save = False
            
            return True, new_value
    
    user = User(name='John Doe')
    assert user.slug == 'john-doe'


def test_logging_hook():
    """Hook can log all changes."""
    
    log = []
    
    class AuditedEntity(Entity):
        value = String()
        
        @staticmethod
        def on_event(entity, field_name, old_value, new_value, action):
            log.append(f"{action}:{field_name}:{old_value}->{new_value}")
            return True, new_value
    
    entity = AuditedEntity(value='initial')
    log.clear()
    
    entity.value = 'updated'
    entity.delete()
    
    assert any(f'{ACTION_MODIFY}:value:initial->updated' in entry for entry in log)
    assert any(f'{ACTION_DELETE}:None:' in entry for entry in log)
