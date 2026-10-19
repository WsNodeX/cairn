"""Command-line interface for Cairn."""

import argparse
import sys
from datetime import datetime

from .parser import CairnError, parse
from .scheduler import next_fire, prev_fire


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cairn",
        description="Compute next/previous fire times for cron expressions.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    for name, help_text in (
        ("next", "Show the next fire time(s)."),
        ("prev", "Show the previous fire time(s)."),
    ):
        sp = sub.add_parser(name, help=help_text)
        sp.add_argument("expr", help="A 5-field cron expression, e.g. '0 0 * * *'")
        sp.add_argument("-n", "--count", type=int, default=1,
                        help="Number of occurrences to print (default: 1)")
        sp.add_argument("-f", "--from", dest="from_", default=None,
                        help="Reference time (ISO 8601, naive). Defaults to now.")

    return parser


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        sched = parse(args.expr)
    except CairnError as exc:
        print(f"cairn: error: {exc}", file=sys.stderr)
        return 2

    base = datetime.now()
    if args.from_:
        try:
            base = datetime.fromisoformat(args.from_)
        except ValueError:
            print(f"cairn: error: invalid --from value: {args.from_!r}",
                  file=sys.stderr)
            return 2

    try:
        t = base
        for _ in range(args.count):
            t = next_fire(sched, t) if args.cmd == "next" else prev_fire(sched, t)
            print(t.isoformat())
    except CairnError as exc:
        print(f"cairn: error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
