import unittest
from datetime import datetime

from cairn.parser import parse
from cairn.scheduler import next_fire, prev_fire, matches


class TestNextFire(unittest.TestCase):
    def test_every_midnight(self):
        s = parse("0 0 * * *")
        self.assertEqual(
            next_fire(s, datetime(2026, 10, 19, 14, 24)),
            datetime(2026, 10, 20, 0, 0),
        )

    def test_specific_time(self):
        s = parse("30 2 * * *")
        self.assertEqual(
            next_fire(s, datetime(2026, 10, 19, 14, 24)),
            datetime(2026, 10, 20, 2, 30),
        )

    def test_every_hour(self):
        s = parse("0 * * * *")
        self.assertEqual(
            next_fire(s, datetime(2026, 10, 19, 14, 24)),
            datetime(2026, 10, 19, 15, 0),
        )

    def test_quarter_hour(self):
        s = parse("*/15 * * * *")
        self.assertEqual(
            next_fire(s, datetime(2026, 10, 19, 14, 24)),
            datetime(2026, 10, 19, 14, 30),
        )

    def test_first_of_month(self):
        s = parse("0 0 1 * *")
        self.assertEqual(
            next_fire(s, datetime(2026, 10, 19, 14, 24)),
            datetime(2026, 11, 1, 0, 0),
        )

    def test_monday(self):
        s = parse("0 0 * * 1")
        # 2026-10-19 is a Monday; next Monday is 2026-10-26.
        self.assertEqual(
            next_fire(s, datetime(2026, 10, 19, 14, 24)),
            datetime(2026, 10, 26, 0, 0),
        )

    def test_or_semantics(self):
        # 13th of month OR every Friday.
        s = parse("0 0 13 * 5")
        # Next Friday after 2026-10-19 is 2026-10-23 (not the 13th).
        self.assertEqual(
            next_fire(s, datetime(2026, 10, 19, 14, 24)),
            datetime(2026, 10, 23, 0, 0),
        )

    def test_same_minute_edge(self):
        s = parse("0 0 * * *")
        self.assertEqual(
            next_fire(s, datetime(2026, 10, 19, 0, 0)),
            datetime(2026, 10, 20, 0, 0),
        )


class TestPrevFire(unittest.TestCase):
    def test_every_midnight(self):
        s = parse("0 0 * * *")
        self.assertEqual(
            prev_fire(s, datetime(2026, 10, 19, 14, 24)),
            datetime(2026, 10, 19, 0, 0),
        )

    def test_or_semantics_prev(self):
        s = parse("0 0 13 * 5")
        # Latest Friday or 13th before 2026-10-19 is 2026-10-16 (Friday).
        self.assertEqual(
            prev_fire(s, datetime(2026, 10, 19, 14, 24)),
            datetime(2026, 10, 16, 0, 0),
        )


class TestMatches(unittest.TestCase):
    def test_matches_true(self):
        s = parse("30 2 * * *")
        self.assertTrue(matches(s, datetime(2026, 10, 19, 2, 30)))

    def test_matches_false(self):
        s = parse("30 2 * * *")
        self.assertFalse(matches(s, datetime(2026, 10, 19, 2, 31)))


if __name__ == "__main__":
    unittest.main()
