import json

from tester import Tester

from kybra_simple_db import *

logger = get_logger()


class TestDatabase:
    def setUp(self):
        self.db = Database.get_instance()
        self.db.clear()

    def test_database_basic_operations(self):
        # Test save and load
        data = {"name": "John", "age": 30}
        self.db.save("person", "1", data)
        loaded = self.db.load("person", "1")
        assert loaded == data

        # Test update
        self.db.update("person", "1", "age", 31)
        loaded = self.db.load("person", "1")
        assert loaded["age"] == 31

        # Test delete
        self.db.delete("person", "1")
        self.db.clear()  # Clear database to ensure data is removed
        assert self.db.load("person", "1") is None

    def test_database_get_all(self):
        data1 = {"name": "John", "age": 30}
        data2 = {"name": "Jane", "age": 25}

        self.db.save("person", "1", data1)
        self.db.save("person", "2", data2)

        all_data = self.db.get_all()
        logger.debug(f"all_data: {all_data}")
        assert len(all_data) == 2
        assert all_data["person@1"] == data1
        assert all_data["person@2"] == data2

    def test_database_dump_json(self):
        # Test empty database
        logger.debug(f"self.db.dump_json(): {self.db.dump_json()}")
        assert self.db.dump_json() == "{}"
        assert json.loads(self.db.dump_json(pretty=True)) == {}

        # Add some test data
        person_data = {"name": "John", "age": 30}
        dept_data = {"name": "IT", "location": "HQ"}

        self.db.save("person", "1", person_data)
        self.db.save("department", "1", dept_data)

        # Test non-pretty output
        dumped = json.loads(self.db.dump_json())
        assert "person" in dumped
        assert "department" in dumped
        assert dumped["person"]["1"] == person_data
        assert dumped["department"]["1"] == dept_data

        # Test pretty output
        pretty_dumped = self.db.dump_json(pretty=True)
        assert "\n" in pretty_dumped
        assert json.loads(pretty_dumped) == dumped


def run():
    print("Running tests...")
    tester = Tester(TestDatabase)
    return tester.run_tests()


if __name__ == "__main__":
    exit(run())
