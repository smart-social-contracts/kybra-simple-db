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
        """Reset database before each test (for Tester runner)."""
        Database.get_instance().clear()

    def setup_method(self):
        """Reset database before each test (for pytest)."""
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

        NamespacedPerson(name="Charlie", age=25)
        NamespacedPerson(name="Diana", age=30)

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
        deserialized = Entity.deserialize(serialized)
        assert deserialized is not None
        assert deserialized.name == "Eve"
        assert deserialized._type == "app::AppUser"

    def test_namespace_relations_same_namespace(self):
        """Test relations between entities in the same namespace."""

        class BlogPost(Entity):
            __namespace__ = "app"
            title = String()
            author = ManyToOne("app::BlogUser", "posts")

        class BlogUser(Entity):
            __namespace__ = "app"
            name = String()
            posts = OneToMany("app::BlogPost", "author")

        user = BlogUser(name="Alice")
        post1 = BlogPost(title="First Post")
        post2 = BlogPost(title="Second Post")

        # Test ManyToOne assignment
        post1.author = user
        assert post1.author == user
        assert post1 in user.posts

        # Test OneToMany assignment
        user.posts = [post1, post2]
        assert list(user.posts) == [post1, post2]
        assert post1.author == user
        assert post2.author == user

    def test_namespace_relations_different_namespaces(self):
        """Test relations between entities in different namespaces."""

        class AppPost(Entity):
            __namespace__ = "app"
            title = String()
            editor = ManyToOne("admin::Editor", "edited_posts")

        class Editor(Entity):
            __namespace__ = "admin"
            name = String()
            edited_posts = OneToMany("app::AppPost", "editor")

        editor = Editor(name="Bob")
        post = AppPost(title="Breaking News")

        # Cross-namespace relation
        post.editor = editor
        assert post.editor == editor
        assert post in editor.edited_posts

    def test_namespace_manytomany_relations(self):
        """Test ManyToMany relations with namespaced entities."""

        class Student(Entity):
            __namespace__ = "school"
            name = String()
            courses = ManyToMany("school::Course", "students")

        class Course(Entity):
            __namespace__ = "school"
            name = String()
            students = ManyToMany("school::Student", "courses")

        student1 = Student(name="Alice")
        student2 = Student(name="Bob")
        course1 = Course(name="Math")
        course2 = Course(name="Science")

        # Assign multiple students to course
        course1.students = [student1, student2]
        assert set(course1.students) == {student1, student2}
        assert course1 in student1.courses
        assert course1 in student2.courses

        # Assign multiple courses to student
        student1.courses = [course1, course2]
        assert set(student1.courses) == {course1, course2}
        assert student1 in course1.students
        assert student1 in course2.students

    def test_namespace_collision_prevention(self):
        """Test that different namespaces prevent type collisions."""

        class Product(Entity):
            __namespace__ = "store"
            name = String()
            price = Integer()

        class Product2(Entity):
            __namespace__ = "warehouse"
            name = String()
            quantity = Integer()

        # Create instances
        store_product = Product(name="Laptop", price=1000)
        warehouse_product = Product2(name="Monitor", quantity=50)

        # Both should be registered independently after instance creation
        db = Database.get_instance()
        assert "store::Product" in db._entity_types
        assert "warehouse::Product2" in db._entity_types

        # Verify they have separate IDs and types
        assert store_product._type == "store::Product"
        assert warehouse_product._type == "warehouse::Product2"
        assert store_product._id == "1"
        assert warehouse_product._id == "1"

    def test_namespace_relation_with_string_id(self):
        """Test that relation resolution works with string IDs for namespaced entities."""

        class Author(Entity):
            __namespace__ = "blog"
            name = String()
            articles = OneToMany("blog::Article", "author")

        class Article(Entity):
            __namespace__ = "blog"
            title = String()
            author = ManyToOne("blog::Author", "articles")

        author = Author(name="Jane")
        article = Article(title="Tech Review")

        # Assign using string ID
        article.author = author._id
        assert article.author == author
        assert article in author.articles

        # Assign using entity instance
        article2 = Article(title="Another Article")
        article2.author = author
        assert article2.author == author
        assert article2 in author.articles


def run(test_name: str = None, test_var: str = None):
    """Run the namespace tests."""
    tester = Tester(TestNamespaces)
    if test_name:
        return tester.run_test(test_name, test_var)
    return tester.run_tests()


if __name__ == "__main__":
    exit(run())
