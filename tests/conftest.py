"""Pytest configuration and fixtures for kybra-simple-db tests."""

import pytest

from kybra_simple_db import Database


@pytest.fixture(autouse=True)
def clear_database():
    """Clear the database before each test to ensure test isolation."""
    try:
        db = Database.get_instance()
        if db is not None:
            db.clear()
    except Exception:
        # If no instance exists yet, that's fine
        pass
    yield
