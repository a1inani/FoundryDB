import time
from foundrydb.storage import StorageEngine

store = StorageEngine("foundries/bench")
start = time.time()
for i in range(10_000):
    store.insert("bench", {"id": i})
print("insert time:", time.time() - start)
print("rows read:", len(list(store.scan("bench"))))
