# tests/test_select.py
from foundrydb import Database

def test_simple_select():
    db = Database()
    db.execute("CREATE TABLE t (x INT);")
    db.execute("INSERT INTO t VALUES (5);")
    assert db.execute("SELECT * FROM t;") == [(5,)]
