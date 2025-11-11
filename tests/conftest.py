import pytest
from foundrydb.database import Database


@pytest.fixture
def new_db(tmp_path):
    return Database(tmp_path / "testdb")
