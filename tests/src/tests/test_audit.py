"""Tests for audit functionality in Kybra Simple DB."""

from kybra_simple_logging import get_logger
from tester import Tester

from kybra_simple_db import *

logger = get_logger(__name__)


class TestAudit:
    def setUp(self):
        self.db = Database.get_instance()
        self.db.clear()

    def tearDown(self):
        """Clean up after each test by resetting the database singleton."""
        self.db.clear()  # Clear the database first
        Database._instance = None  # Then reset the singleton

    def test_audit_initialization(self):
        """Test if the audit database is initialized correctly."""
        assert self.db._db_audit is not None

    def test_audit_log_save_operation(self):
        """Test if a save operation is logged correctly in the audit database."""
        self.db.save("test_type", "1", {"field": "value"})
        audit_log = self.db._db_audit.get("0")
        assert audit_log is not None
        assert "save" in audit_log

    def test_audit_log_delete_operation(self):
        """Test if a delete operation is logged correctly in the audit database."""
        self.db.save("test_type", "1", {"field": "value"})
        self.db.delete("test_type", "1")
        audit_log = self.db._db_audit.get("1")
        assert audit_log is not None
        assert "delete" in audit_log

    def test_audit_log_update_operation(self):
        """Test if an update operation is logged correctly in the audit database."""
        self.db.save("test_type", "1", {"field": "value"})
        self.db.update("test_type", "1", "field", "new_value")
        audit_log = self.db._db_audit.get("2")
        assert audit_log is not None
        assert "update" in audit_log

    def test_get_audit_functionality(self):
        """Test the get_audit functionality that retrieves audit records by ID range."""
        # Clear any existing data
        self.db.clear()

        # Create a Person entity that will generate an audit record
        person_data = {
            "name": "John",
            "age": 30,
            "creator": "system",
            "owner": "system",
            "updater": "system",
        }
        self.db.save("Person", "1", person_data)

        # Get audit records with ID range 0-5
        audit_records = self.db.get_audit(id_from=0, id_to=5)

        # Print the actual record for debugging
        logger.debug(f"Audit records: {audit_records}")
        if "0" in audit_records:
            logger.debug(f"First audit record: {audit_records['0']}")
            if len(audit_records["0"]) >= 4:
                logger.debug(f"Entity data: {audit_records['0'][3]}")

        # Verify we have at least one audit record
        assert audit_records is not None
        assert "0" in audit_records

        # Verify the structure of the first audit record
        audit_record = audit_records["0"]
        assert audit_record is not None
        assert (
            len(audit_record) == 4
        )  # Should have 4 elements: operation, timestamp, entity_id, entity_data

        # Verify the audit record fields
        assert audit_record[0] == "save"  # First element should be the operation type
        assert isinstance(audit_record[1], int)  # Second element should be a timestamp
        assert (
            audit_record[2] == "Person@1"
        )  # Third element should be the entity identifier

        # Check entity data exists with expected fields
        entity_data = audit_record[3]
        assert entity_data is not None
        assert "name" in entity_data
        assert entity_data["name"] == "John"
        assert "age" in entity_data
        assert entity_data["age"] == 30

    def test_no_audit_when_disabled(self):
        """Test that no audit records are created when audit_enabled is False."""
        # Create a new database instance with audit_enabled=False
        Database._instance = None  # Reset the singleton
        db_no_audit = Database.init(audit_enabled=False)

        # Clear any existing data
        db_no_audit.clear()

        # Perform operations that would normally create audit records
        person_data = {
            "name": "Alice",
            "age": 25,
            "creator": "system",
            "owner": "system",
            "updater": "system",
        }

        # Save operation
        db_no_audit.save("Person", "1", person_data)

        # Update operation
        db_no_audit.update("Person", "1", "age", 26)

        # Delete operation
        db_no_audit.delete("Person", "1")

        # Verify that no audit records were created
        # The _db_audit attribute should be None when audit_enabled=False
        assert db_no_audit._db_audit is None


def run(test_name: str = None, test_var: str = None):
    tester = Tester(TestAudit)
    return tester.run_tests()


if __name__ == "__main__":
    exit(run())
