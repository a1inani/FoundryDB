import pytest
from pathlib import Path
from foundrydb.storage import StorageEngine

def test_table_insert_and_persist(tmp_path):
    """Insert rows and verify file persistence"""
    storage = StorageEngine(tmp_path)
    table_name = "users"
    rows = [{"id": 1, "name": "Alice"}]

    storage.insert(table_name, rows[0])

    file_path = tmp_path / f"{table_name}.tbl"
    assert file_path.exists()
    assert file_path.stat().st_size > 0

def test_scan_reads_back_inserted_rows(tmp_path):
    """Rows written should be read back exactly."""
    storage = StorageEngine(tmp_path)
    table_name = "users"
    rows = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

    for row in rows:
        storage.insert(table_name, row)

    result = list(storage.scan(table_name))
    assert result == rows