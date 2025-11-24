"""Simple hook system for entity modifications.

Entities can define an on_event static method to intercept and control changes:

    from kybra_simple_db import Entity, String, ACTION_MODIFY
    
    class User(Entity):
        name = String()
        
        @staticmethod
        def on_event(entity, field_name, old_value, new_value, action):
            # action: ACTION_CREATE, ACTION_MODIFY, or ACTION_DELETE
            # Returns: (allow: bool, modified_value: any)
            
            if action == ACTION_MODIFY and field_name == 'name':
                return True, new_value.upper()  # Auto-capitalize
            
            return True, new_value
"""

from typing import Tuple, Any, Optional

from .constants import ACTION_CREATE, ACTION_MODIFY, ACTION_DELETE


def call_entity_hook(entity, field_name: Optional[str], old_value: Any, 
                     new_value: Any, action: str) -> Tuple[bool, Any]:
    """Call entity's on_event hook if defined.
    
    Args:
        entity: Entity instance
        field_name: Field being changed (None for entity-level actions)
        old_value: Previous value
        new_value: New value  
        action: ACTION_CREATE, ACTION_MODIFY, or ACTION_DELETE
        
    Returns:
        (allow: bool, modified_value: Any)
    """
    if hasattr(entity.__class__, 'on_event'):
        hook = entity.__class__.on_event
        if callable(hook):
            result = hook(entity, field_name, old_value, new_value, action)
            
            if isinstance(result, tuple) and len(result) == 2:
                return result
            elif isinstance(result, bool):
                return result, new_value
    
    return True, new_value
