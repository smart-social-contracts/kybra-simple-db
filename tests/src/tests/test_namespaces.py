"""Simple test demonstrating namespace functionality in Kybra Simple DB.

This test shows how entities can be organized into namespaces to avoid
type conflicts when you have multiple entities with the same class name.
"""

from tester import Tester

from kybra_simple_db import *


# Entities without namespace (default behavior)
class User(Entity):
    """Standard user entity without namespace."""

    name = String(min_length=1, max_length=100)
    email = String()


# Entities with different namespaces
class AppUser(Entity):
    """User entity in the 'app' namespace."""

    __namespace__ = "app"
    name = String(min_length=1, max_length=100)
    email = String()
    role = String()


class AdminUser(Entity):
    """User entity in the 'admin' namespace."""

    __namespace__ = "admin"
    name = String(min_length=1, max_length=100)
    email = String()
    permissions = String()


class TestNamespaces:
    """Test suite for namespace functionality."""

    def setUp(self):
        """Reset database before each test."""
        Database.get_instance().clear()

    def test_basic_namespace_storage(self):
        """Test that namespaced entities are stored correctly."""
        # Create entities with same class name but different namespaces
        app_user = AppUser(name="Alice", email="alice@app.com", role="developer")
        admin_user = AdminUser(name="Bob", email="bob@admin.com", permissions="all")

        # Verify they have different type names
        assert app_user._type == "app::AppUser"
        assert admin_user._type == "admin::AdminUser"

        # Verify they can be loaded independently
        loaded_app = AppUser.load(app_user._id)
        loaded_admin = AdminUser.load(admin_user._id)

        assert loaded_app is not None
        assert loaded_admin is not None
        assert loaded_app.name == "Alice"
        assert loaded_admin.name == "Bob"

        # Verify they have separate ID sequences
        assert app_user._id == "1"
        assert admin_user._id == "1"  # Each namespace has its own counter

    def test_namespace_isolation(self):
        """Test that entities in different namespaces don't interfere."""
        # Create multiple users in different namespaces with same IDs
        app1 = AppUser(name="App User 1", email="app1@test.com", role="user")
        admin1 = AdminUser(
            name="Admin User 1", email="admin1@test.com", permissions="read"
        )
        regular1 = User(name="Regular User 1", email="regular1@test.com")

        # All should have ID "1" in their respective namespaces
        assert app1._id == "1"
        assert admin1._id == "1"
        assert regular1._id == "1"

        # Verify counts are separate
        assert AppUser.count() == 1
        assert AdminUser.count() == 1
        assert User.count() == 1

        # Verify they don't interfere with each other
        assert AppUser.load("1").name == "App User 1"
        assert AdminUser.load("1").name == "Admin User 1"
        assert User.load("1").name == "Regular User 1"

    def test_namespace_with_alias(self):
        """Test that aliases work correctly with namespaces."""

        class NamespacedPerson(Entity):
            __namespace__ = "people"
            __alias__ = "name"
            name = String()
            age = Integer()

        person1 = NamespacedPerson(name="Charlie", age=25)
        person2 = NamespacedPerson(name="Diana", age=30)

        # Should be able to lookup by alias
        found = NamespacedPerson["Charlie"]
        assert found is not None
        assert found.name == "Charlie"
        assert found.age == 25

        # Verify alias key includes namespace
        alias_key = NamespacedPerson._alias_key()
        assert alias_key == "people::NamespacedPerson_alias"

    def test_mixed_namespace_and_regular(self):
        """Test mixing namespaced and regular entities."""
        # Regular entity without namespace
        user1 = User(name="Regular", email="regular@test.com")

        # Namespaced entities
        app1 = AppUser(name="App", email="app@test.com", role="dev")
        admin1 = AdminUser(name="Admin", email="admin@test.com", permissions="write")

        # All should work independently
        assert User.count() == 1
        assert AppUser.count() == 1
        assert AdminUser.count() == 1

        # Verify full type names
        assert user1._type == "User"
        assert app1._type == "app::AppUser"
        assert admin1._type == "admin::AdminUser"

    def test_namespace_serialization(self):
        """Test that namespaced entities serialize/deserialize correctly."""
        app_user = AppUser(name="Eve", email="eve@test.com", role="admin")
        serialized = app_user.serialize()

        # Verify namespace is in serialized type
        assert serialized["_type"] == "app::AppUser"
        assert serialized["name"] == "Eve"

        # Deserialize should work
        db = Database.get_instance()
        deserialized = Entity.deserialize(serialized)
        assert deserialized is not None
        assert deserialized.name == "Eve"
        assert deserialized._type == "app::AppUser"


def run(test_name: str = None, test_var: str = None):
    """Run the namespace tests."""
    tester = Tester(TestNamespaces)
    return tester.run_test(test_name, test_var)


if __name__ == "__main__":
    exit(run())
