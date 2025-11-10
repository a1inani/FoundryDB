# FoundryDB

<p align="center">
  <img src="assets/banner.png" width="50%" />
</p>

**A tiny educational SQL engine written in pure Python.**

FoundryDB is a personal experimental project to explore how relational database systems actually work under the hood. From parsing SQL, to planning, to storage and tuple access.

This is not production-grade software. It's a playground.

---

## Goals

- Teach myself the internal moving parts of a DBMS
- Be small enough to understand in a single sitting
- Pure Python
- Transparent / readable code > performance

---

## Non-goals

- Competing with SQLite or Postgres
- Correctness for all SQL edge cases
- Maximizing speed

---

## Rough architecture (planned)

| Layer | Responsibility |
|---|---|
| **Lexer/Parser** | tokenize & parse SQL into AST |
| **Planner** | validate AST + generate logical plans |
| **Execution Engine** | run plans against storage |
| **Storage** | page format, files, catalog, indexes (maybe later) |

---

## Roadmap ideas

- `SELECT` with projections + simple `WHERE` + other DDL and DML commands
- Disk-backed heap file manager
- Simple B-Tree index (stretch goal)
- Minimal transaction log + recovery (stretch goal)

---

## Requirements

- Python ≥ 3.11

---

## License

This project is licensed under the MIT License.

See [`LICENSE`](./LICENSE) for details.
