"""Compute next/previous fire times for a parsed :class:`Schedule`."""

from datetime import datetime, timedelta

from .errors import CairnError
from .parser import Schedule

# Safety bound: never scan more than eight years into the past or future.
_HORIZON_DAYS = 366 * 8


def _cron_dow(dt: datetime) -> int:
    """Map a Python weekday (Mon=0..Sun=6) to cron dow (Sun=0..Sat=6)."""
    return (dt.weekday() + 1) % 7


def matches(sched: Schedule, dt: datetime) -> bool:
    """Return True if ``dt`` satisfies the schedule."""
    if dt.minute not in sched.minutes:
        return False
    if dt.hour not in sched.hours:
        return False
    if dt.month not in sched.months:
        return False

    dom_ok = dt.day in sched.doms
    dow_ok = _cron_dow(dt) in sched.dows

    # Vixie-cron semantics: when both day-of-month and day-of-week are
    # restricted, the job fires if EITHER matches (OR). When only one is
    # restricted, they are ANDed.
    if sched.dom_is_star or sched.dow_is_star:
        return dom_ok and dow_ok
    return dom_ok or dow_ok


def _advance_day(t: datetime, sched: Schedule) -> datetime:
    return t.replace(
        hour=min(sched.hours), minute=min(sched.minutes),
        second=0, microsecond=0,
    ) + timedelta(days=1)


def next_fire(sched: Schedule, after: datetime) -> datetime:
    """Return the first fire time strictly after ``after``."""
    t = after.replace(second=0, microsecond=0) + timedelta(minutes=1)
    limit = t + timedelta(days=_HORIZON_DAYS)

    while t < limit:
        if t.minute not in sched.minutes:
            cands = [m for m in sorted(sched.minutes) if m > t.minute]
            if cands:
                t = t.replace(minute=cands[0], second=0, microsecond=0)
            else:
                t = t.replace(minute=min(sched.minutes), second=0, microsecond=0) \
                    + timedelta(hours=1)
            continue
        if t.hour not in sched.hours:
            cands = [h for h in sorted(sched.hours) if h > t.hour]
            if cands:
                t = t.replace(hour=cands[0], minute=min(sched.minutes),
                              second=0, microsecond=0)
            else:
                t = _advance_day(t, sched)
            continue
        if not matches(sched, t):
            t = _advance_day(t, sched)
            continue
        return t

    raise CairnError("No matching time within the search horizon")


def _rewind_day(t: datetime, sched: Schedule) -> datetime:
    return t.replace(
        hour=max(sched.hours), minute=max(sched.minutes),
        second=0, microsecond=0,
    ) - timedelta(days=1)


def prev_fire(sched: Schedule, before: datetime) -> datetime:
    """Return the last fire time strictly before ``before``."""
    t = before.replace(second=0, microsecond=0) - timedelta(minutes=1)
    limit = t - timedelta(days=_HORIZON_DAYS)

    while t > limit:
        if t.minute not in sched.minutes:
            cands = [m for m in sorted(sched.minutes) if m < t.minute]
            if cands:
                t = t.replace(minute=cands[-1], second=0, microsecond=0)
            else:
                t = t.replace(minute=max(sched.minutes), second=0, microsecond=0) \
                    - timedelta(hours=1)
            continue
        if t.hour not in sched.hours:
            cands = [h for h in sorted(sched.hours) if h < t.hour]
            if cands:
                t = t.replace(hour=cands[-1], minute=max(sched.minutes),
                              second=0, microsecond=0)
            else:
                t = _rewind_day(t, sched)
            continue
        if not matches(sched, t):
            t = _rewind_day(t, sched)
            continue
        return t

    raise CairnError("No matching time within the search horizon")
