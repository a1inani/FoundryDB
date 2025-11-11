from foundrydb.storage import StorageEngine


def test_corrupt_trailing_bytes(tmp_path):
    storage = StorageEngine(tmp_path)
    table = "users"
    storage.insert(table, {"id": 1})
    # manually corrupt file
    with open(tmp_path / f"{table}.tbl", "ab") as f:
        f.write(b"{bad json line\n")
    rows = list(storage.scan(table))
    assert rows == [{"id": 1}]
