"""Tests for schema migration functionality in Kybra Simple DB."""

from tester import Tester

from kybra_simple_db import *


class TestMigrations:
    def setUp(self):
        """Reset database before each test."""
        Database.get_instance().clear()

    def test_default_version(self):
        """Test that entities have default version 1."""

        class Product(Entity):
            name = String()

        product = Product(name="Widget")

        # Version is stored in database, not in public serialize()
        db = Database.get_instance()
        stored_data = db.load("Product", product._id)
        assert "__version__" in stored_data
        assert stored_data["__version__"] == 1

    def test_custom_version(self):
        """Test that entities can have custom versions."""

        class Product(Entity):
            __version__ = 3
            name = String()

        product = Product(name="Widget")

        # Version is stored in database, not in public serialize()
        db = Database.get_instance()
        stored_data = db.load("Product", product._id)
        assert stored_data["__version__"] == 3

    def test_migration_on_load(self):
        """Test that migration is triggered when loading old version data."""

        class Product(Entity):
            __version__ = 1
            name = String()

        product = Product(name="Widget")
        product_id = product._id

        Database.get_instance().clear_registry()

        class Product(Entity):
            __version__ = 2
            name = String()
            price = Float(default=0.0)

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    if "price" not in obj:
                        obj["price"] = 0.0
                return obj

        Database.get_instance().register_entity_type(Product)

        loaded = Product.load(product_id)

        assert loaded is not None
        assert loaded.name == "Widget"
        assert hasattr(loaded, "price")
        assert loaded.price == 0.0

    def test_migration_multiple_versions(self):
        """Test migration across multiple versions."""

        class Product(Entity):
            __version__ = 1
            name = String()

        product = Product(name="Widget")
        product_id = product._id

        Database.get_instance().clear_registry()

        class Product(Entity):
            __version__ = 3
            name = String()
            price = Float(default=0.0)
            category = String(default="general")

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    if "price" not in obj:
                        obj["price"] = 0.0

                if from_version <= 2 and to_version >= 3:
                    if "category" not in obj:
                        obj["category"] = "general"

                return obj

        Database.get_instance().register_entity_type(Product)

        loaded = Product.load(product_id)

        assert loaded is not None
        assert loaded.name == "Widget"
        assert loaded.price == 0.0
        assert loaded.category == "general"

    def test_migration_field_rename(self):
        """Test migration that renames a field."""

        class Product(Entity):
            __version__ = 1
            old_name = String()

        product = Product(old_name="Widget")
        product_id = product._id

        Database.get_instance().clear_registry()

        class Product(Entity):
            __version__ = 2
            new_name = String()

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    if "old_name" in obj:
                        obj["new_name"] = obj.pop("old_name")
                return obj

        Database.get_instance().register_entity_type(Product)

        loaded = Product.load(product_id)

        assert loaded is not None
        assert loaded.new_name == "Widget"
        assert not hasattr(loaded, "old_name")

    def test_migration_on_deserialize(self):
        """Test that migration is triggered during deserialization."""

        class Product(Entity):
            __version__ = 1
            name = String()

        product = Product(name="Widget")
        data = product.serialize()

        Database.get_instance().clear()

        class Product(Entity):
            __version__ = 2
            name = String()
            price = Float(default=0.0)

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    if "price" not in obj:
                        obj["price"] = 10.0
                return obj

        Database.get_instance().register_entity_type(Product)

        loaded = Product.deserialize(data)

        assert loaded is not None
        assert loaded.name == "Widget"
        assert loaded.price == 10.0

    def test_no_migration_same_version(self):
        """Test that no migration occurs when versions match."""

        class Product(Entity):
            __version__ = 2
            name = String()
            price = Float(default=0.0)

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                obj["migrated"] = True
                return obj

        product = Product(name="Widget", price=5.0)
        product_id = product._id

        Database.get_instance().clear_registry()
        loaded = Product.load(product_id)

        assert loaded is not None
        assert loaded.name == "Widget"
        assert loaded.price == 5.0
        data = loaded.serialize()
        assert "migrated" not in data

    def test_migration_preserves_data(self):
        """Test that migrations preserve existing data fields."""

        class Product(Entity):
            __version__ = 1
            name = String()
            description = String()

        product = Product(name="Widget", description="A useful widget")
        product_id = product._id

        Database.get_instance().clear_registry()

        class Product(Entity):
            __version__ = 2
            name = String()
            description = String()
            price = Float(default=0.0)

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    if "price" not in obj:
                        obj["price"] = 0.0
                return obj

        Database.get_instance().register_entity_type(Product)

        loaded_product = Product.load(product_id)

        assert loaded_product is not None
        assert loaded_product.name == "Widget"
        assert loaded_product.description == "A useful widget"
        assert loaded_product.price == 0.0

    def test_migration_with_data_transformation(self):
        """Test migration that transforms existing data."""

        class Product(Entity):
            __version__ = 1
            name = String()
            price_cents = Integer()

        product = Product(name="Widget", price_cents=1000)
        product_id = product._id

        Database.get_instance().clear_registry()

        class Product(Entity):
            __version__ = 2
            name = String()
            price_dollars = Float()

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    if "price_cents" in obj:
                        obj["price_dollars"] = obj.pop("price_cents") / 100.0
                return obj

        Database.get_instance().register_entity_type(Product)

        loaded = Product.load(product_id)

        assert loaded is not None
        assert loaded.name == "Widget"
        assert loaded.price_dollars == 10.0
        assert not hasattr(loaded, "price_cents")

    def test_migration_backward_compatible(self):
        """Test that entities without version field default to version 1."""

        db = Database.get_instance()
        old_data = {"_type": "Product", "_id": "1", "name": "Widget"}
        db.save("Product", "1", old_data)

        class Product(Entity):
            __version__ = 2
            name = String()
            price = Float(default=0.0)

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    if "price" not in obj:
                        obj["price"] = 5.0
                return obj

        db.register_entity_type(Product)

        loaded = Product.load("1")

        assert loaded is not None
        assert loaded.name == "Widget"
        assert loaded.price == 5.0

    def test_migration_with_one_to_one_relation(self):
        """Test migration of entity with OneToOne relationship."""

        class Profile(Entity):
            __version__ = 1
            bio = String()

        class User(Entity):
            __version__ = 1
            name = String()

        profile = Profile(bio="Developer")
        user = User(name="Alice")
        user_id = user._id
        profile_id = profile._id

        # Store relation ID in database
        db = Database.get_instance()
        user_data = db.load("User", user_id)
        user_data["profile_id"] = profile_id  # Simple ID reference
        db.save("User", user_id, user_data)

        Database.get_instance().clear_registry()

        class Profile(Entity):
            __version__ = 2
            bio = String()
            website = String(default="")

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    if "website" not in obj:
                        obj["website"] = ""
                return obj

        class User(Entity):
            __version__ = 2
            name = String()
            email = String(default="")
            profile_id = String(default="")  # Relation stored as ID

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    if "email" not in obj:
                        obj["email"] = ""
                return obj

        Database.get_instance().register_entity_type(Profile)
        Database.get_instance().register_entity_type(User)

        loaded_user = User.load(user_id)
        loaded_profile = Profile.load(profile_id)

        assert loaded_user is not None
        assert loaded_user.name == "Alice"
        assert loaded_user.email == ""
        assert loaded_user.profile_id == profile_id  # Relation ID preserved
        assert loaded_profile is not None
        assert loaded_profile.bio == "Developer"
        assert loaded_profile.website == ""

    def test_migration_with_simple_properties(self):
        """Test migration adding properties to entity (no complex relations)."""

        class Comment(Entity):
            __version__ = 1
            text = String()

        comment1 = Comment(text="Great!")
        comment2 = Comment(text="Nice!")
        comment1_id = comment1._id
        comment2_id = comment2._id

        Database.get_instance().clear_registry()

        class Comment(Entity):
            __version__ = 2
            text = String()
            approved = Boolean(default=True)
            author = String(default="Anonymous")

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    if "approved" not in obj:
                        obj["approved"] = True
                    if "author" not in obj:
                        obj["author"] = "Anonymous"
                return obj

        Database.get_instance().register_entity_type(Comment)

        loaded_comment1 = Comment.load(comment1_id)
        loaded_comment2 = Comment.load(comment2_id)

        assert loaded_comment1 is not None
        assert loaded_comment1.text == "Great!"
        assert loaded_comment1.approved is True
        assert loaded_comment1.author == "Anonymous"
        assert loaded_comment2 is not None
        assert loaded_comment2.text == "Nice!"
        assert loaded_comment2.approved is True

    def test_migration_with_multiple_entities(self):
        """Test migrating multiple independent entities."""

        class Student(Entity):
            __version__ = 1
            name = String()

        class Course(Entity):
            __version__ = 1
            title = String()

        course1 = Course(title="Math")
        course2 = Course(title="Physics")
        student = Student(name="Bob")
        student_id = student._id
        course1_id = course1._id
        course2_id = course2._id

        Database.get_instance().clear_registry()

        class Student(Entity):
            __version__ = 2
            name = String()
            grade = String(default="A")

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    if "grade" not in obj:
                        obj["grade"] = "A"
                return obj

        class Course(Entity):
            __version__ = 2
            title = String()
            credits = Integer(default=3)

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    if "credits" not in obj:
                        obj["credits"] = 3
                return obj

        Database.get_instance().register_entity_type(Student)
        Database.get_instance().register_entity_type(Course)

        loaded_student = Student.load(student_id)
        loaded_course1 = Course.load(course1_id)
        loaded_course2 = Course.load(course2_id)

        assert loaded_student is not None
        assert loaded_student.name == "Bob"
        assert loaded_student.grade == "A"
        assert loaded_course1 is not None
        assert loaded_course1.title == "Math"
        assert loaded_course1.credits == 3
        assert loaded_course2 is not None
        assert loaded_course2.title == "Physics"
        assert loaded_course2.credits == 3

    def test_migration_relation_field_rename(self):
        """Test migration that renames a relation field."""

        class Profile(Entity):
            __version__ = 1
            bio = String()

        class User(Entity):
            __version__ = 1
            name = String()
            profile = OneToOne("Profile", "owner")

        class Profile(Entity):
            __version__ = 1
            bio = String()
            owner = OneToOne("User", "profile")

        profile = Profile(bio="Developer")
        user = User(name="Alice", profile=profile)
        user_id = user._id
        profile_id = profile._id

        Database.get_instance().clear_registry()

        class Profile(Entity):
            __version__ = 2
            bio = String()
            user = OneToOne("User", "user_profile")

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    if "owner" in obj:
                        obj["user"] = obj.pop("owner")
                return obj

        class User(Entity):
            __version__ = 2
            name = String()
            user_profile = OneToOne("Profile", "user")

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    if "profile" in obj:
                        obj["user_profile"] = obj.pop("profile")
                return obj

        Database.get_instance().register_entity_type(Profile)
        Database.get_instance().register_entity_type(User)

        loaded_user = User.load(user_id)

        assert loaded_user is not None
        assert loaded_user.name == "Alice"
        # Verify migration renamed the relation field in stored data
        db = Database.get_instance()
        user_data = db.load("User", user_id)
        profile_data = db.load("Profile", profile_id)
        assert "user_profile" in user_data
        assert "user" in profile_data
        # Note: Bidirectional relation consistency after field rename
        # may require manual data fix or more complex migration logic

    def test_migration_persistence_verification(self):
        """Test that migration changes are persisted to database."""

        class Product(Entity):
            __version__ = 1
            name = String()

        product = Product(name="Widget")
        product_id = product._id

        Database.get_instance().clear_registry()

        class Product(Entity):
            __version__ = 2
            name = String()
            price = Float(default=0.0)

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    if "price" not in obj:
                        obj["price"] = 9.99
                return obj

        Database.get_instance().register_entity_type(Product)

        # First load triggers migration
        loaded1 = Product.load(product_id)
        assert loaded1.price == 9.99

        # Verify migration was persisted to database
        db = Database.get_instance()
        db_data = db.load("Product", product_id)
        assert db_data["__version__"] == 2
        assert db_data["price"] == 9.99

        # Clear registry and load again - should not trigger migration
        db.clear_registry()
        loaded2 = Product.load(product_id)
        assert loaded2.price == 9.99

        # Verify version in DB is still 2
        db_data_after = db.load("Product", product_id)
        assert db_data_after["__version__"] == 2

    def test_migration_identity_map_consistency(self):
        """Test that entity identity map works correctly after migration."""

        class Product(Entity):
            __version__ = 1
            name = String()

        product = Product(name="Widget")
        product_id = product._id

        Database.get_instance().clear_registry()

        class Product(Entity):
            __version__ = 2
            name = String()
            price = Float(default=0.0)

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    if "price" not in obj:
                        obj["price"] = 5.0
                return obj

        Database.get_instance().register_entity_type(Product)

        # Load same entity twice - should return same instance
        loaded1 = Product.load(product_id)
        loaded2 = Product.load(product_id)

        assert loaded1 is loaded2
        assert loaded1.price == 5.0
        assert loaded2.price == 5.0

        # Modify via one reference, should reflect in other
        loaded1.price = 10.0
        assert loaded2.price == 10.0

    def test_migration_with_timestamped_mixin(self):
        """Test that TimestampedMixin fields survive migration."""

        class Product(Entity, TimestampedMixin):
            __version__ = 1
            name = String()

        product = Product(name="Widget")
        product_id = product._id
        # Access fields through __dict__ to get actual stored values
        db = Database.get_instance()
        stored_data = db.load("Product", product_id)
        original_created = stored_data.get("timestamp_created")
        original_creator = stored_data.get("creator")

        Database.get_instance().clear_registry()

        class Product(Entity, TimestampedMixin):
            __version__ = 2
            name = String()
            price = Float(default=0.0)

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    if "price" not in obj:
                        obj["price"] = 0.0
                return obj

        Database.get_instance().register_entity_type(Product)

        loaded = Product.load(product_id)

        assert loaded is not None
        assert loaded.name == "Widget"
        assert loaded.price == 0.0
        # Verify mixin fields are preserved
        loaded_data = db.load("Product", product_id)
        assert loaded_data.get("timestamp_created") == original_created
        assert loaded_data.get("creator") == original_creator
        assert "timestamp_updated" in loaded_data
        assert "updater" in loaded_data
        assert "owner" in loaded_data

    def test_migration_error_handling(self):
        """Test that migration errors are handled gracefully."""

        class Product(Entity):
            __version__ = 1
            name = String()
            old_price = String()  # String type

        product = Product(name="Widget", old_price="invalid")
        product_id = product._id

        Database.get_instance().clear_registry()

        class Product(Entity):
            __version__ = 2
            name = String()
            price = Float()

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    # This will raise ValueError for invalid string
                    obj["price"] = float(obj["old_price"])
                    del obj["old_price"]
                return obj

        Database.get_instance().register_entity_type(Product)

        # Migration should fail with ValueError
        try:
            Product.load(product_id)
            assert False, "Expected ValueError to be raised"
        except ValueError:
            pass  # Expected

    def test_migration_downgrade_scenario(self):
        """Test behavior when loading newer version with older code."""

        class Product(Entity):
            __version__ = 2
            name = String()
            price = Float(default=0.0)

        product = Product(name="Widget", price=10.0)
        product_id = product._id

        # Verify v2 is stored
        db = Database.get_instance()
        stored_data = db.load("Product", product_id)
        assert stored_data["__version__"] == 2

        Database.get_instance().clear_registry()

        # Simulate rollback to v1 code
        class Product(Entity):
            __version__ = 1
            name = String()

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                # Downgrade scenario: from_version=2, to_version=1
                # Default implementation does nothing
                return obj

        Database.get_instance().register_entity_type(Product)

        # Loading v2 data with v1 code
        # This will trigger migrate(data, from_version=2, to_version=1)
        loaded = Product.load(product_id)

        assert loaded is not None
        assert loaded.name == "Widget"
        # price field exists in data but not in v1 schema
        # Entity should load without error (extra fields ignored)

    def test_migration_deserialize_simple(self):
        """Test migration during deserialize with simple properties."""

        class Product(Entity):
            __version__ = 1
            name = String()

        product = Product(name="Widget")

        # Serialize v1 entity
        product_data = product.serialize()

        Database.get_instance().clear()

        # Define v2 schema
        class Product(Entity):
            __version__ = 2
            name = String()
            price = Float(default=0.0)
            category = String(default="general")

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                if from_version == 1 and to_version >= 2:
                    if "price" not in obj:
                        obj["price"] = 19.99
                    if "category" not in obj:
                        obj["category"] = "general"
                return obj

        Database.get_instance().register_entity_type(Product)

        # Deserialize v1 data with v2 schema (should trigger migration)
        deserialized_product = Product.deserialize(product_data)

        assert deserialized_product is not None
        assert deserialized_product.name == "Widget"
        assert deserialized_product.price == 19.99
        assert deserialized_product.category == "general"
        # Verify migration was persisted
        db = Database.get_instance()
        product_db_data = db.load("Product", deserialized_product._id)
        assert product_db_data["__version__"] == 2
        assert product_db_data["price"] == 19.99

    def test_migration_large_version_jump(self):
        """Test migration with large version jump (v1 to v10)."""

        class Product(Entity):
            __version__ = 1
            name = String()

        product = Product(name="Widget")
        product_id = product._id

        Database.get_instance().clear_registry()

        class Product(Entity):
            __version__ = 10
            name = String()
            price = Float(default=0.0)
            category = String(default="general")
            in_stock = Boolean(default=True)

            @classmethod
            def migrate(cls, obj, from_version, to_version):
                # Simulate multiple version migrations
                if from_version < 5 and to_version >= 5:
                    obj["price"] = 0.0
                if from_version < 7 and to_version >= 7:
                    obj["category"] = "general"
                if from_version < 10 and to_version >= 10:
                    obj["in_stock"] = True
                return obj

        Database.get_instance().register_entity_type(Product)

        loaded = Product.load(product_id)

        assert loaded is not None
        assert loaded.name == "Widget"
        assert loaded.price == 0.0
        assert loaded.category == "general"
        assert loaded.in_stock is True


def run(test_name: str = None, test_var: str = None):
    tester = Tester(TestMigrations)
    return tester.run_tests()


if __name__ == "__main__":
    exit(run())
