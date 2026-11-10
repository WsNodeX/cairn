<p align="center">
  <em>Mark the moments your code runs.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/WsNodeX/cairn?style=flat-square&color=111111&label=stars" alt="Stars">
  <img src="https://img.shields.io/github/v/release/WsNodeX/cairn?style=flat-square&color=111111&label=release" alt="Release">
  <img src="https://img.shields.io/badge/license-MIT-111111?style=flat-square" alt="MIT">
</p>

---

A cron expression parser and scheduler in pure Python. It answers the two
questions that matter: **when does this next fire?** and **when did it last fire?**

## Quick start

```python
from datetime import datetime
from cairn import parse, next_fire

schedule = parse("0 0 * * 1-5")     # midnight, weekdays only
print(next_fire(schedule, datetime(2026, 10, 19, 14, 24)))
# -> 2026-10-20 00:00:00
```

```bash
cairn next "*/15 * * * *" -n 3                    # next three fire times
cairn prev "0 2 * * *" -f 2026-10-19T14:00:00     # last fire before a reference
```

## Why this instead of `croniter`

- **Zero dependencies.** Standard library only — droppable into a locked-down
  production image.
- **Real Vixie-cron semantics.** Day-of-month and day-of-week are `OR`-ed, not
  `AND`-ed. Sunday is both `0` and `7`. Named months and weekdays, steps, stepped
  ranges and lists all work.
- **Deterministic.** Given a reference time, `next_fire` and `prev_fire` always
  return the same instant. No drift, no hidden clock reads.

## Supported syntax

| Feature | Example | Meaning |
| --- | --- | --- |
| Any value | `*` | Every unit |
| Ranges | `9-17` | Inclusive span |
| Steps | `*/15` | Every 15 units from the minimum |
| Stepped range | `9/3` | From 9, stepping by 3, to the maximum |
| Lists | `0,30` | Union of values |
| Named months | `JAN` | January |
| Named weekdays | `MON` | Monday |
| `?` wildcard | `? * * *` | "Any" for the day fields |

## Install

```bash
pip install cairn
```

Or copy the `cairn/` directory into your project — it needs nothing beyond the
standard library.

## API

| Function | Returns |
|---|---|
| `parse(expr)` | `Schedule` with a precomputed value set per field; raises `CairnError` on malformed input |
| `next_fire(schedule, after)` | First instant strictly after `after` |
| `prev_fire(schedule, before)` | Last instant strictly before `before` |
| `matches(schedule, dt)` | Whether `dt` satisfies the schedule |

## How it works

```mermaid
graph LR
  E["0 0 * * 1-5"] --> P[parser.parse]
  P -->|Schedule: sets per field| S[scheduler]
  S -->|next_fire / prev_fire| D[datetime]
```

Deliberately linear: `parse` turns text into a `Schedule` with precomputed value
sets, and `scheduler` answers questions against that structure with a bounded
forward or backward scan. There is no daemon, no thread, no event loop — you ask,
it answers.

## Tests

```bash
python -m unittest discover -s tests
```

CI runs the suite on Python 3.8 through 3.13 on every push.

## Limitations

- **Naive datetimes only.** No timezone-aware scheduling yet; convert at the edges.
- **You drive the clock.** Cairn computes times, it does not run your job — pair it
  with `sched`, `asyncio`, or a system timer.
- **No `@daily`-style macros yet.** Use the 5-field form.

## License

MIT
