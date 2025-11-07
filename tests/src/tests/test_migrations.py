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

        data = product.serialize()
        assert "__version__" in data
        assert data["__version__"] == 1

    def test_custom_version(self):
        """Test that entities can have custom versions."""

        class Product(Entity):
            __version__ = 3
            name = String()

        product = Product(name="Widget")

        data = product.serialize()
        assert data["__version__"] == 3

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


def run(test_name: str = None, test_var: str = None):
    tester = Tester(TestMigrations)
    return tester.run_tests()


if __name__ == "__main__":
    exit(run())
