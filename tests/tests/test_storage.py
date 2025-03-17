from tester import Tester

from kybra_simple_db import *


class TestStorage:
    def test_memory_storage_basic_operations(self):
        storage = MemoryStorage()

        # Test insert and get
        storage.insert("key1", "value1")
        assert storage.get("key1") == "value1"
        assert "key1" in storage

        # Test non-existent key
        assert storage.get("non_existent") is None
        assert "non_existent" not in storage

        # Test remove
        storage.insert("key2", "value2")
        assert "key2" in storage
        storage.remove("key2")
        assert "key2" not in storage

        # Test items
        storage.insert("key3", "value3")
        storage.insert("key4", "value4")
        items = dict(storage.items())
        assert items == {"key1": "value1", "key3": "value3", "key4": "value4"}


    def test_memory_storage_remove_nonexistent(self):
        storage = MemoryStorage()
        Tester.assert_raises(KeyError, storage.remove, "non_existent")


    def test_memory_storage_clear(self):
        storage = MemoryStorage()
        storage.insert("key1", "value1")
        storage.insert("key2", "value2")

        assert "key1" in storage
        assert "key2" in storage

        storage.clear()

        assert "key1" not in storage
        assert "key2" not in storage
        assert dict(storage.items()) == {}


def run():
    print("Running tests...")
    tester = Tester(TestStorage)
    return tester.run_tests()

if __name__ == "__main__":
    exit(run())
