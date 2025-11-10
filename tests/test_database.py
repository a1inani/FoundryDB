import pytest
from pathlib import Path
from foundrydb.database import Database

@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary FoundryDB instance."""
    db = Database("demo")
    yield db

def test_database_initialization(temp_db):
    db = temp_db
    assert db.path.exists()
    assert db.catalog is not None
    assert db.storage is not None

def test_execute_returns_list(temp_db):
    """execute() should return a list even if empty"""
    result = temp_db.execute("SELECT * FROM users;")
    assert isinstance(result, list)

def test_insert_and_scan(tmp_path):
    """Simulate table insert/scan operations."""
    from foundrydb.storage import StorageEngine

    storage = StorageEngine(tmp_path)
    rows = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

    for row in rows:
        storage.insert("users", row)

    all_rows = list(storage.scan("users"))
    assert len(all_rows) == 2
    assert all_rows[0]["id"] == 1