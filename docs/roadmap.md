# FoundryDB — Technical Roadmap

> Scope: an educational, embedded SQL engine in pure Python. Ship value early, grow capabilities incrementally, keep code small and readable.

## Versioning Plan

* **v0.1**: Phases 1–2 (storage + minimal SELECT/WHERE)
* **v0.2**: Phases 3–5 (schema + CRUD + single‑column indexes)
* **v0.3**: Phase 6 (page storage + buffer pool)
* **v0.4**: Phases 7–8 (JOINs + aggregates)
* **v0.5**: Phase 9 (basic transactions)
* **v0.6**: Phase 10 (optimizer)
* **v0.7**: Phase 11–12 (advanced indexes + concurrency)
* **v0.8+**: Phases 13–15 (constraints, views/subqueries, advanced features)

---

## Phase 1: Core Storage Engine (v0.1)

**Goal:** Persist rows to disk and read them back with a tiny programmatic API.

**Deliverables**

* File format: CSV‑like or fixed‑width records (choose 1; document tradeoffs in `specs/storage.md`).
* API: `Table.insert(row)`, `Table.scan()` (returns iterable of rows).
* Module: `foundrydb/storage.py` with a `Table` abstraction.

**Key Tasks**

* Define row layout & simple serializer/deserializer.
* Implement append‑only writer; sequential reader.
* Minimal error handling (I/O errors, malformed rows).

**Acceptance Tests**

* Insert 10k rows; scan returns all rows in order.
* Restart process; scan still returns all rows.
* Corrupt trailing bytes → reader stops safely (no crash).

**Notes**

* Prefer CSV for readability *or* fixed‑width for consistent offsets. Start simple—indexes/transactions come later.

---

## Phase 2: Simple Query Language (v0.1)

**Goal:** Run `SELECT ... FROM table WHERE ...` (no JOINs) by scanning.

**Deliverables**

* Mini parser for a subset of SQL: `SELECT <cols> FROM <table> [WHERE <pred>]`.
* Expression evaluator for equality/relational ops on literals & columns.
* Executor that performs full table scan + filter + projection.

**Key Tasks**

* Define an internal IR (AST) for `Select`, `Column`, `Literal`, `Compare`.
* Write a small hand‑rolled parser (or Lark) for the subset grammar.
* Implement executor: scan → predicate filter → project columns.

**Acceptance Tests**

* Basic projections: `SELECT id,name FROM t`.
* WHERE operators: `=, !=, <, <=, >, >=` on INT/VARCHAR.
* Unknown column or table ⇒ friendly error.

**Notes**

* Keep grammar file in `grammar/foundrydb.ebnf` for future growth.

---

## Phase 3: Data Types & Schema Management (v0.2)

**Goal:** Typed columns and persisted catalog.

**Deliverables**

* Types: `INT`, `VARCHAR(N)`, `FLOAT`, `DATE` (start with INT, VARCHAR; stub others).
* Catalog file storing table schemas + simple bootstrap.
* SQL: `CREATE TABLE`, `DROP TABLE`.
* Type validation on insert.

**Key Tasks**

* Catalog module (`foundrydb/catalog.py`) with `create_table`, `drop_table`, `load_schema`.
* Extend storage to validate per schema.
* Parser: add DDL statements.

**Acceptance Tests**

* Create, insert valid/invalid rows, drop.
* Persist and reload catalog across process restarts.

**Notes**

* Keep VARCHAR bounded; enforce at insert time.

---

## Phase 4: Basic Indexing (v0.2)

**Goal:** Speed up simple lookups using a single‑column index.

**Deliverables**

* B‑tree **or** hash index (choose one to start; B‑tree is more general).
* SQL: `CREATE INDEX idx_name ON t(col)`.
* Executor uses index for `WHERE col = <value>` when available.
* Index maintenance on `INSERT`/`DELETE`.

**Key Tasks**

* Index module (`foundrydb/index.py`) with pluggable interface.
* Maintain index file mapping key → record pointer (file offset / (page,slot) later).
* Simple cost check: prefer index if predicate is equality on indexed column.

**Acceptance Tests**

* With/without index: time deltas show improvement on point lookups.
* Consistency: index finds the same rows as full scan.

**Notes**

* Defer range scans until B‑tree is stable.

---

## Phase 5: INSERT, UPDATE, DELETE (v0.2)

**Goal:** Full CRUD via SQL for single tables.

**Deliverables**

* SQL: `INSERT INTO`, `UPDATE ... WHERE`, `DELETE ... WHERE`.
* Index updates on mutations.

**Key Tasks**

* Row locator design (temp: byte offset; after Phase 6: (page,slot)).
* Implement in‑place update *or* append‑only with tombstones (document choice).
* Ensure index maintenance mirrors data changes.

**Acceptance Tests**

* CRUD round‑trip correctness on random datasets.
* Index remains consistent post‑updates/deletes.

**Notes**

* Append‑only + tombstones keeps it simple now; compaction can come later.

---

## Phase 6: Page‑Based Storage (v0.3)

**Goal:** Move to fixed‑size pages with a small buffer pool.

**Deliverables**

* Page format (e.g., 4 KB) with header + slot directory.
* Buffer pool with LRU eviction; page pin/unpin API.
* Update row locator to (page_id, slot_id).

**Key Tasks**

* `storage/page.py`, `storage/buffer_pool.py`.
* Migrate table scan/insert/update to page APIs.
* Write simple page cache metrics for debugging.

**Acceptance Tests**

* Random read/write workload; no data loss; basic performance gain over raw file.
* Survive unclean shutdown (fsync on page flushes for now).

**Notes**

* Sets foundation for WAL and transactions in Phase 9.

---

## Phase 7: Multi‑Table Queries (JOINs) (v0.4)

**Goal:** Support basic joins.

**Deliverables**

* SQL: `SELECT ... FROM A INNER JOIN B ON A.k = B.k`.
* Executor: nested loop join (start), optional index‑nested‑loop when index exists.
* Table aliases.

**Key Tasks**

* Parser: JOIN syntax & ON predicates.
* Execute plan: join operator node with left/right child cursors.

**Acceptance Tests**

* Correctness on equi‑joins; aliasing works; column disambiguation.

**Notes**

* Defer hash join/sort‑merge until optimizer (Phase 10).

---

## Phase 8: Aggregations & Grouping (v0.4)

**Goal:** Basic analytic queries.

**Deliverables**

* Aggregates: `COUNT, SUM, AVG, MIN, MAX`.
* `GROUP BY`, `HAVING`, `ORDER BY`, `LIMIT`.

**Key Tasks**

* Implement aggregate operators; grouping with hash table.
* Sort utility (in‑memory; later external sort if needed).

**Acceptance Tests**

* Aggregation correctness on known datasets.
* ORDER BY stable; LIMIT exact.

**Notes**

* Keep memory limits in mind; spill later if necessary.

---

## Phase 9: Basic Transactions (v0.5)

**Goal:** Recoverability & atomicity for single‑process usage.

**Deliverables**

* `BEGIN`, `COMMIT`, `ROLLBACK`.
* Write‑Ahead Logging (WAL) with redo on crash.
* Simple write locks to avoid concurrent write conflicts (single process).

**Key Tasks**

* WAL record types for insert/update/delete.
* Log manager; recovery routine on startup (REDO; optional UNDO if needed).

**Acceptance Tests**

* Crash during update → recover to committed state.
* Rollback restores pre‑txn state.

**Notes**

* Keep concurrency simple until Phase 12.

---

## Phase 10: Query Optimization (v0.6)

**Goal:** Choose better plans automatically.

**Deliverables**

* Cost model: rows, selectivity, index hinting.
* Plan enumeration for single‑table access path (scan vs index).
* Join order heuristic (left‑deep trees; small → large).

**Key Tasks**

* Statistics collection (per table/column histograms or simple counts/distincts).
* Planner that annotates costs & picks cheapest.

**Acceptance Tests**

* Queries choose index when selective; scans when not.
* Multi‑table queries change join order appropriately on skewed data.

**Notes**

* Keep the optimizer tiny and transparent; document in `specs/optimizer.md`.

---

## Phase 11: Advanced Indexes (v0.7)

**Goal:** More indexing power.

**Deliverables**

* Composite (multi‑column) indexes.
* Partial indexes (`CREATE INDEX ... WHERE ...`).
* Index‑only scans when covering.

**Key Tasks**

* Extend index key schema; support prefix/range in planner.
* Executor: detect covering plans to skip table lookups.

**Acceptance Tests**

* Composite index used for predicates on leading columns.
* Partial index ignored when predicate outside its WHERE.

---

## Phase 12: Concurrency Control (v0.7)

**Goal:** Correct concurrent reads/writes.

**Deliverables**

* MVCC **or** row‑level locks (choose one; MVCC recommended for readers‑don’t‑block‑readers).
* Deadlock detection or timeout policy.

**Key Tasks**

* Transaction IDs, visibility rules (MVCC snapshots), or lock manager.
* Integrate with WAL.

**Acceptance Tests**

* Concurrent readers don’t block; writers serialize safely.
* Deadlocks resolved by victim selection.

---

## Phase 13: Constraints & Foreign Keys (v0.8)

**Goal:** Declarative integrity.

**Deliverables**

* `PRIMARY KEY`, `UNIQUE`, `NOT NULL`.
* `FOREIGN KEY` with `ON DELETE/UPDATE` behaviors.
* `CHECK` constraints.

**Key Tasks**

* Enforce on insert/update; index PK/UNIQUE automatically.
* FK validation on write; cascading actions.

**Acceptance Tests**

* Violations raise clear errors; cascading behaves as configured.

---

## Phase 14: Views & Subqueries (v0.8)

**Goal:** Composability and reuse.

**Deliverables**

* `CREATE VIEW` (stored query text + expansion at parse/plan time).
* Subqueries in `WHERE` and `FROM` (derived tables).
* Correlated subqueries (initially via nested loops).

**Key Tasks**

* Parser support; planner expansion rules; alias scoping.

**Acceptance Tests**

* View definition & usage; subquery correctness on test cases.

---

## Phase 15: Advanced Features (v0.9+)

**Menu:**

* Full‑text search index (tokenization + inverted index).
* `JSON` column type with basic path ops.
* Stored procedures/functions (Python UDFs first).
* Triggers (row‑level before/after hooks).
* Replication/backup (offline snapshot → later streaming).

---

## Cross‑Cutting Quality Bars

* **Docs:** `specs/` notes per phase; keep `README` examples runnable.
* **Tests:** Pytest suite with property tests for storage/index; golden tests for parser.
* **CLI:** `foundrydb-cli` REPL once SELECT/INSERT stable (v0.2).
* **Perf harness:** simple benchmark scripts with reproducible datasets.
* **Error messages:** friendly, precise, actionable.

## Nice‑to‑Have Utilities

* `EXPLAIN` output for plans; `PRAGMA` style knobs for debug.
* Data importer for CSV.

## Out of Scope (for now)

* Network server / authentication.
* Distributed execution.
* Advanced SQL dialect features beyond the phases above.

---

### Getting Started Checklist (maintainer)

* [ ] Create `specs/` files for storage, parser, catalog, optimizer.
* [ ] Add minimal `docs/examples/` scripts that reflect current phase.
* [ ] Set up `pytest`, `ruff`, `mypy` (optional) in CI.
* [ ] Add `EXPLAIN` stub and `--debug` logging switches.

> Keep it small. Optimize for learning and clarity first; performance and completeness later.
