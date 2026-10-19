"""Cairn — a zero-dependency cron expression parser and scheduler.

Cairn turns a standard 5-field cron expression into a deterministic schedule
and answers the two questions that matter most: *when does this next fire?*
and *when did it last fire?*
"""

from .errors import CairnError
from .parser import Schedule, parse
from .scheduler import next_fire, prev_fire, matches

__version__ = "0.1.0"
__all__ = [
    "CairnError",
    "Schedule",
    "parse",
    "next_fire",
    "prev_fire",
    "matches",
]
