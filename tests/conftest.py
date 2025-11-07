"""Pytest configuration and fixtures for kybra-simple-db tests."""

import pytest

from kybra_simple_db import Database


@pytest.fixture(autouse=True)
def clear_database():
    """Clear the database before each test to ensure test isolation."""
    if Database._instance is not None:
        Database._instance.clear()
    yield
