"""Tests for audit functionality in Kybra Simple DB."""

from tester import Tester

from kybra_simple_db import *
from kybra_simple_db import logger


class TestAudit:
    def setUp(self):
        self.db = Database.get_instance()
        self.db.clear()

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
        logger.debug(f'self.db._db_audit.get("0"): {self.db._db_audit.get("0")}')
        logger.debug(f'self.db._db_audit.get("1"): {self.db._db_audit.get("1")}')
        logger.debug(f'self.db._db_audit.get("2"): {self.db._db_audit.get("2")}')
        logger.debug(f'self.db._db_audit.get("3"): {self.db._db_audit.get("3")}')
        logger.debug(f'self.db._db_audit.get("4"): {self.db._db_audit.get("4")}')
        logger.debug(f'self.db._db_audit.get("5"): {self.db._db_audit.get("5")}')
        assert audit_log is not None
        assert "delete" in audit_log

    def test_audit_log_update_operation(self):
        """Test if an update operation is logged correctly in the audit database."""
        self.db.save("test_type", "1", {"field": "value"})
        self.db.update("test_type", "1", "field", "new_value")
        audit_log = self.db._db_audit.get("2")
        logger.debug(f'self.db._db_audit.get("0"): {self.db._db_audit.get("0")}')
        logger.debug(f'self.db._db_audit.get("1"): {self.db._db_audit.get("1")}')
        logger.debug(f'self.db._db_audit.get("2"): {self.db._db_audit.get("2")}')
        logger.debug(f'self.db._db_audit.get("3"): {self.db._db_audit.get("3")}')
        logger.debug(f'self.db._db_audit.get("4"): {self.db._db_audit.get("4")}')
        logger.debug(f'self.db._db_audit.get("5"): {self.db._db_audit.get("5")}')
        assert audit_log is not None
        assert "update" in audit_log


def run():
    logger.debug("Running tests...")
    tester = Tester(TestAudit)
    return tester.run_tests()


if __name__ == "__main__":
    exit(run())
