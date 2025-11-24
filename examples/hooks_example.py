"""Example usage of the on_event hook system.

This demonstrates how to use the on_event hook to:
- Validate data before it's saved
- Transform values automatically
- Prevent deletion of protected entities
- Track changes for auditing
"""

from kybra_simple_db import (
    Database, Entity, String, Integer,
    ACTION_CREATE, ACTION_MODIFY, ACTION_DELETE
)


# Example 1: Validation
class User(Entity):
    username = String()
    email = String()
    age = Integer()
    
    @staticmethod
    def on_event(entity, field_name, old_value, new_value, action):
        """Validate user data before saving."""
        
        # Username must be at least 3 characters
        if field_name == 'username' and new_value:
            if len(new_value) < 3:
                return False, None  # Reject
        
        # Email must contain @
        if field_name == 'email' and new_value:
            if '@' not in new_value:
                return False, None  # Reject
        
        # Age must be between 0 and 150
        if field_name == 'age' and new_value is not None:
            if new_value < 0 or new_value > 150:
                return False, None  # Reject
        
        return True, new_value  # Allow


# Example 2: Automatic transformation
class Product(Entity):
    name = String()
    price = Integer()
    
    @staticmethod
    def on_event(entity, field_name, old_value, new_value, action):
        """Auto-capitalize name and ensure positive price."""
        
        # Auto-capitalize product names
        if field_name == 'name' and new_value:
            return True, new_value.upper()
        
        # Ensure price is positive
        if field_name == 'price' and new_value is not None:
            if new_value < 0:
                return True, 0  # Set to 0 instead
        
        return True, new_value


# Example 3: Protected deletion
class Account(Entity):
    name = String()
    is_protected = Integer()
    
    @staticmethod
    def on_event(entity, field_name, old_value, new_value, action):
        """Prevent deletion of protected accounts."""
        
        if action == ACTION_DELETE and entity.is_protected == 1:
            print(f"Cannot delete protected account: {entity.name}")
            return False, None  # Prevent deletion
        
        return True, new_value


# Example 4: Audit trail
audit_log = []

class AuditedDocument(Entity):
    title = String()
    content = String()
    
    @staticmethod
    def on_event(entity, field_name, old_value, new_value, action):
        """Log all changes to documents."""
        
        if action == ACTION_MODIFY and field_name:
            audit_log.append({
                'entity_id': entity._id,
                'field': field_name,
                'old_value': old_value,
                'new_value': new_value
            })
        
        if action == ACTION_DELETE:
            audit_log.append({
                'entity_id': entity._id,
                'action': 'deleted',
                'title': entity.title
            })
        
        return True, new_value


if __name__ == '__main__':
    db = Database.get_instance()
    db.clear()
    
    print("=== Example 1: Validation ===")
    try:
        user = User(username='ab', email='test@example.com', age=25)
    except ValueError as e:
        print(f"✓ Rejected short username: {e}")
    
    user = User(username='john_doe', email='john@example.com', age=25)
    print(f"✓ Valid user created: {user.username}")
    
    try:
        user.email = 'invalid-email'
    except ValueError as e:
        print(f"✓ Rejected invalid email: {e}")
    
    print("\n=== Example 2: Transformation ===")
    product = Product(name='widget', price=-10)
    print(f"✓ Name auto-capitalized: {product.name}")
    print(f"✓ Negative price corrected: {product.price}")
    
    print("\n=== Example 3: Protected deletion ===")
    admin = Account(name='Admin', is_protected=1)
    try:
        admin.delete()
    except PermissionError as e:
        print(f"✓ Protected account deletion prevented: {e}")
    
    guest = Account(name='Guest', is_protected=0)
    guest.delete()
    print(f"✓ Non-protected account deleted")
    
    print("\n=== Example 4: Audit trail ===")
    doc = AuditedDocument(title='Report', content='Initial content')
    audit_log.clear()
    
    doc.content = 'Updated content'
    doc.title = 'Final Report'
    
    print(f"✓ Logged {len(audit_log)} changes:")
    for entry in audit_log:
        print(f"  - {entry}")
    
    db.clear()
