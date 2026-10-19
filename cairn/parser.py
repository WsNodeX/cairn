"""Parse standard 5-field cron expressions into structured schedules.

Supported syntax per field:
  *           any value
  ?           any value (only valid for day-of-month / day-of-week)
  a-b         inclusive range
  a/b         range starting at a stepping by b (a defaults to the field minimum)
  a-b/c       range a..b stepping by c
  x,y,z       comma-separated union of the above

Field bounds:
  minute        0-59
  hour          0-23
  day-of-month  1-31
  month         1-12   (JAN-DEC also accepted)
  day-of-week   0-7    (0 and 7 both mean Sunday; SUN-SAT also accepted)
"""

from dataclasses import dataclass

from .errors import CairnError

MONTH_NAMES = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}

DOW_NAMES = {
    "SUN": 0, "MON": 1, "TUE": 2, "WED": 3, "THU": 4, "FRI": 5, "SAT": 6,
}

# (low, high) for each of the five fields.
FIELD_BOUNDS = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]


@dataclass
class Schedule:
    """A parsed cron schedule with precomputed value sets for each field."""

    minutes: set
    hours: set
    doms: set
    months: set
    dows: set
    expr: str
    dom_is_star: bool
    dow_is_star: bool


def _resolve(token: str, allow_names: bool, names: dict) -> int:
    token = token.strip().upper()
    if allow_names and token in names:
        return names[token]
    if token.lstrip("-").isdigit():
        return int(token)
    raise CairnError(f"Invalid field value: {token!r}")


def _parse_field(field, low, high, allow_names=False, names=None,
                 question_is_star=False):
    field = field.strip()
    if question_is_star and field == "?":
        field = "*"
    if field == "":
        raise CairnError("Empty cron field")

    result = set()
    for part in field.split(","):
        part = part.strip()
        if part == "":
            raise CairnError(f"Empty segment in field: {field!r}")

        if "/" in part:
            base, step_s = part.split("/", 1)
            try:
                step = int(step_s)
            except ValueError:
                raise CairnError(f"Invalid step: {step_s!r}")
            if step < 1:
                raise CairnError(f"Step must be >= 1: {part!r}")
        else:
            base, step = part, 1

        base = base.strip()
        if base == "*":
            rng = range(low, high + 1, step)
        elif "-" in base:
            a_s, b_s = base.split("-", 1)
            a = _resolve(a_s, allow_names, names)
            b = _resolve(b_s, allow_names, names)
            if a > b:
                raise CairnError(f"Range start greater than end: {base!r}")
            rng = range(a, b + 1, step)
        else:
            v = _resolve(base, allow_names, names)
            rng = range(v, v + 1) if step == 1 else range(v, high + 1, step)

        for value in rng:
            if value < low or value > high:
                raise CairnError(
                    f"Value {value} out of range [{low},{high}] in {field!r}"
                )
            # In cron, both 0 and 7 denote Sunday.
            result.add(0 if (high == 7 and value == 7) else value)

    if not result:
        raise CairnError(f"Empty field after parsing: {field!r}")
    return result


def parse(expr: str) -> Schedule:
    """Parse a cron expression into a :class:`Schedule`."""
    fields = expr.split()
    if len(fields) != 5:
        raise CairnError(
            f"Expected 5 fields, got {len(fields)} in {expr!r}"
        )

    minute = _parse_field(fields[0], *FIELD_BOUNDS[0])
    hour = _parse_field(fields[1], *FIELD_BOUNDS[1])
    dom_field = fields[2]
    month = _parse_field(fields[3], *FIELD_BOUNDS[3], allow_names=True, names=MONTH_NAMES)
    dow_field = fields[4]
    dom = _parse_field(dom_field, *FIELD_BOUNDS[2], question_is_star=True)
    dow = _parse_field(
        dow_field, *FIELD_BOUNDS[4], allow_names=True,
        names=DOW_NAMES, question_is_star=True,
    )

    return Schedule(
        minutes=minute,
        hours=hour,
        doms=dom,
        months=month,
        dows=dow,
        expr=expr,
        dom_is_star=(dom_field.strip() in ("*", "?")),
        dow_is_star=(dow_field.strip() in ("*", "?")),
    )
