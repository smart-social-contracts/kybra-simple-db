import pytest

from kybra_simple_db import *


def test_memory_storage_basic_operations():
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


def test_memory_storage_remove_nonexistent():
    storage = MemoryStorage()
    with pytest.raises(KeyError):
        storage.remove("non_existent")


def test_memory_storage_clear():
    storage = MemoryStorage()
    storage.insert("key1", "value1")
    storage.insert("key2", "value2")

    assert "key1" in storage
    assert "key2" in storage

    storage.clear()

    assert "key1" not in storage
    assert "key2" not in storage
    assert dict(storage.items()) == {}
