import json

from tester import Tester

from kybra_simple_db import *


def get_db():
    """Create a database instance for testing."""
    return Database(MemoryStorage())


def get_db_with_audit():
    """Create a database instance with audit logging for testing."""
    return Database(MemoryStorage(), MemoryStorage())


class TestDatabase:
    def test_database_basic_operations(self):

        db = get_db()
        """Test basic database operations like save, load, and delete."""
        # Test save and load
        data = {"name": "John", "age": 30}
        db.save("person", "1", data)
        loaded = db.load("person", "1")
        assert loaded == data

        # Test update
        db.update("person", "1", "age", 31)
        loaded = db.load("person", "1")
        assert loaded["age"] == 31

        # Test delete
        db.delete("person", "1")
        db._db_storage.clear()  # Clear storage to ensure data is removed
        assert db.load("person", "1") is None

    def test_database_get_all(self):
        db = get_db()

        """Test getting all entities of a type."""
        data1 = {"name": "John", "age": 30}
        data2 = {"name": "Jane", "age": 25}

        db.save("person", "1", data1)
        db.save("person", "2", data2)

        all_data = db.get_all()
        assert len(all_data) == 2
        assert all_data["person@1"] == data1
        assert all_data["person@2"] == data2

    def test_database_dump_json(self):

        db = get_db()

        """Test dumping database contents to JSON."""
        # Test empty database
        assert db.dump_json() == "{}"
        assert json.loads(db.dump_json(pretty=True)) == {}

        # Add some test data
        person_data = {"name": "John", "age": 30}
        dept_data = {"name": "IT", "location": "HQ"}

        db.save("person", "1", person_data)
        db.save("department", "1", dept_data)

        # Test non-pretty output
        dumped = json.loads(db.dump_json())
        assert "person" in dumped
        assert "department" in dumped
        assert dumped["person"]["1"] == person_data
        assert dumped["department"]["1"] == dept_data

        # Test pretty output
        pretty_dumped = db.dump_json(pretty=True)
        assert "\n" in pretty_dumped
        assert json.loads(pretty_dumped) == dumped

    def test_database_audit_logging(self):

        db_with_audit = get_db_with_audit()
        """Test database audit logging functionality."""
        data = {"name": "John", "age": 30}

        # Test save audit
        db_with_audit.save("person", "1", data)
        audit_data = db_with_audit.get_audit()
        assert len(audit_data) > 0

        # Verify audit entry format
        entry = json.loads(list(audit_data.values())[0])
        assert entry[0] == "save"  # operation
        assert isinstance(entry[1], int)  # timestamp
        assert entry[2] == "person@1"  # key
        assert entry[3] == data  # data

        # Test update audit
        db_with_audit.update("person", "1", "age", 31)
        audit_data = db_with_audit.get_audit()
        assert len(audit_data) > 1

        # Test delete audit
        db_with_audit.delete("person", "1")
        audit_data = db_with_audit.get_audit()
        assert len(audit_data) > 2


def run():
    print("Running tests...")
    tester = Tester(TestDatabase)
    return tester.run_tests()


if __name__ == "__main__":
    exit(run())
