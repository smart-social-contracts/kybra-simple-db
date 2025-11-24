"""Simple access control example using on_event hooks and context manager."""

from kybra_simple_db import ACTION_MODIFY, ACTION_DELETE, Database, Entity, String
from kybra_simple_db.mixins import TimestampedMixin


class Document(Entity, TimestampedMixin):
    """Document that only the owner can modify."""

    title = String()
    content = String()

    @staticmethod
    def on_event(entity, field_name, old_value, new_value, action):
        from kybra_simple_db.context import get_caller_id

        caller_id = get_caller_id()

        # Check ownership for modifications and deletions
        if action in (ACTION_MODIFY, ACTION_DELETE):
            if entity._owner != caller_id:
                print(f"❌ {caller_id} cannot modify {entity._owner}'s document")
                return False, None

        return True, new_value


if __name__ == "__main__":
    db = Database.get_instance()
    db.clear()

    print("=== Simple Access Control Demo ===\n")

    # Alice creates a document
    with db.as_user("alice"):
        doc = Document(title="My Doc", content="Secret")
        print(f"✓ Alice created doc (owner: {doc._owner})")

        # Alice can edit her own document
        doc.content = "Updated"
        print("✓ Alice updated her doc")

    # Bob cannot edit Alice's document
    with db.as_user("bob"):
        try:
            doc.content = "Hacked!"
        except ValueError:
            print("✓ Bob was blocked from editing Alice's doc")

        # Bob can create his own document
        bob_doc = Document(title="Bob's Doc", content="Bob's content")
        print(f"✓ Bob created his own doc (owner: {bob_doc._owner})")

    # Admin with as_user can act as anyone
    print("\n=== Nested Context Demo ===")
    with db.as_user("system"):
        system_doc = Document(title="System Doc", content="System")
        print(f"✓ System created doc (owner: {system_doc._owner})")

        with db.as_user("admin"):
            admin_doc = Document(title="Admin Doc", content="Admin")
            print(f"✓ Admin created doc (owner: {admin_doc._owner})")

        # Back to system context
        another_doc = Document(title="Another System Doc", content="System2")
        print(f"✓ System created another doc (owner: {another_doc._owner})")

    db.clear()
    print("\n✓ Demo completed!")
