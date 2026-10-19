<div align="center">

# Cairn

### A zero-dependency cron expression parser and scheduler for Python

*Mark the moments your code runs.*

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)](https://github.com/WsNodeX/cairn)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/WsNodeX/cairn/actions/workflows/ci.yml/badge.svg)](https://github.com/WsNodeX/cairn/actions/workflows/ci.yml)

</div>

---

Cairn parses standard 5-field cron expressions and answers the two questions
that matter most: **when does this next fire?** and **when did it last fire?**
It is pure Python, ships with zero third-party dependencies, and is covered by
a unit-test suite that runs on every Python release from 3.8 to 3.13.

## ✨ Why Cairn

- **No dependencies.** Uses only the Python standard library — drop it in
  anywhere, from a tiny script to a locked-down production image.
- **Correct by default.** Implements true Vixie-cron day-of-month / day-of-week
  `OR` semantics, Sunday-as-`0`-and-`7`, named months and weekdays, and steps.
- **Deterministic.** Given a reference time, `next_fire` / `prev_fire` always
  return the same instant — no surprises, no drift.
- **Tested everywhere.** CI exercises Python 3.8 through 3.13 on every push.

## 🚀 Features

| Feature | Example | Meaning |
| --- | --- | --- |
| Any value | `*` | Every unit |
| Ranges | `9-17` | Inclusive span |
| Steps | `*/15` | Every 15 units from the minimum |
| Stepped range | `9/3` | From 9 stepping by 3 to the maximum |
| Lists | `0,30` | Union of values |
| Named months | `JAN` | January |
| Named weekdays | `MON` | Monday |
| `?` wildcard | `? * * *` | "Any" for day fields |

## 📦 Installation

```bash
pip install cairn
```

Or copy the `cairn/` package directory into your project — it has no
dependencies beyond the standard library.

## ⚡ Quick Start

```python
from datetime import datetime
from cairn import parse, next_fire

schedule = parse("0 0 * * 1-5")  # midnight, weekdays only
print(next_fire(schedule, datetime(2026, 10, 19, 14, 24)))
# -> 2026-10-20 00:00:00
```

Command line:

```bash
# Next 3 fire times for "every 15 minutes"
cairn next "*/15 * * * *" -n 3

# Previous fire time from a specific reference
cairn prev "0 2 * * *" -f 2026-10-19T14:00:00
```

## 🏗️ Architecture

```
            ┌─────────────────────────────┐
  expr ───► │         parser.parse        │
            │  "0 0 * * 1-5"              │
            │                             │
            │  minutes  → {0}             │
            │  hours    → {0}             │
            │  doms     → {1..31}         │
            │  months   → {1..12}         │
            │  dows     → {1,2,3,4,5}     │
            └───────────────┬─────────────┘
                            │  Schedule
                            ▼
            ┌─────────────────────────────┐
            │      scheduler.matches      │  does a datetime fit?
            │      scheduler.next_fire    │  first fire after t
            │      scheduler.prev_fire    │  last fire before t
            └───────────────┬─────────────┘
                            │
                            ▼
                  datetime  (naive, local)
```

The pipeline is deliberately linear: **parse** turns text into a structured
`Schedule` (precomputed value sets per field), and **scheduler** answers
questions against that structure with a bounded forward/backward scan.

## 🔌 API

### `parse(expr: str) -> Schedule`
Parse a 5-field cron expression. Raises `CairnError` on anything malformed
(wrong field count, out-of-range values, reversed ranges, …).

### `next_fire(schedule, after: datetime) -> datetime`
The first instant **strictly after** `after` that satisfies the schedule.
Raises `CairnError` only if no match exists within an 8-year horizon (practically
never for valid expressions).

### `prev_fire(schedule, before: datetime) -> datetime`
The last instant **strictly before** `before` that satisfies the schedule.

### `matches(schedule, dt: datetime) -> bool`
Whether `dt` satisfies the schedule (useful for testing a candidate time).

## 🧭 Roadmap

- [ ] Human-readable `describe()` summaries (`"At 00:00 on every weekday"`)
- [ ] Optional timezone-aware scheduling
- [ ] `@yearly` / `@monthly` / `@daily` macros
- [ ] `cairn check` to validate an expression and pretty-print its fields

## 🤝 Contributing

Bug reports and pull requests are welcome. Run the test suite locally with:

```bash
python -m unittest discover -s tests
```

Please keep the dependency-free promise: changes should not require new
third-party packages.

## 📄 License

Released under the [MIT License](LICENSE).
