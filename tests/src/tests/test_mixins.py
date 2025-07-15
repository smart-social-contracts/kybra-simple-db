"""Test cases for entity mixins."""

import os

from tester import Tester

from kybra_simple_db import *


class TestEntity(Entity, TimestampedMixin):
    """Test entity class that uses TimestampedMixin."""

    pass


class TestMixins:
    def setUp(self):
        """Reset Entity class variables before each test."""
        Database.get_instance().clear()

    def test_timestamped_mixin(self):
        """Test that TimestampedMixin adds timestamp and ownership functionality."""
        # Set up test caller and time
        os.environ["CALLER_ID"] = "test_user"
        system_time = SystemTime.get_instance()

        # Set initial time
        initial_time = 1000000  # 1000 seconds since epoch
        system_time.set_time(initial_time)

        # Create and save entity
        entity = TestEntity()
        entity._save()

        # Check timestamps and ownership
        assert entity._timestamp_created == initial_time
        assert entity._timestamp_updated == initial_time
        assert entity._creator == "test_user"
        assert entity._updater == "test_user"
        assert entity._owner == "test_user"

        # Update entity
        system_time.advance_time(
            60000
        )  # Advance time by 1 minute (60 seconds = 60,000 milliseconds)
        entity._save()

        # Check that updated timestamp changed
        assert entity._timestamp_updated == initial_time + 60000
        assert entity._timestamp_created == initial_time

        # Try to update with different user
        os.environ["CALLER_ID"] = "other_user"
        Tester.assert_raises(PermissionError, entity._save)

        # Change owner and update
        entity.set_owner("other_user")
        system_time.advance_time(60000)  # Advance time by another minute
        entity._save()  # Should work now

        # Verify changes in dictionary format
        data = entity.to_dict()
        assert "timestamp_created" in data
        assert "timestamp_updated" in data
        assert "creator" in data
        assert "updater" in data
        assert "owner" in data
        assert data["creator"] == "test_user"
        assert data["updater"] == "other_user"
        assert data["owner"] == "other_user"

        # Clean up
        system_time.clear_time()


def run(test_name: str = None, test_var: str = None):
    tester = Tester(TestMixins)
    return tester.run_tests()


if __name__ == "__main__":
    exit(run())
