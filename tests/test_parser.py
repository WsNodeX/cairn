import unittest

from cairn.errors import CairnError
from cairn.parser import parse


class TestParseBasic(unittest.TestCase):
    def test_every_day_midnight(self):
        s = parse("0 0 * * *")
        self.assertEqual(s.minutes, {0})
        self.assertEqual(s.hours, {0})
        self.assertEqual(s.doms, set(range(1, 32)))
        self.assertEqual(s.months, set(range(1, 13)))
        self.assertEqual(s.dows, set(range(0, 7)))
        self.assertTrue(s.dom_is_star)
        self.assertTrue(s.dow_is_star)

    def test_step(self):
        s = parse("*/15 * * * *")
        self.assertEqual(s.minutes, {0, 15, 30, 45})

    def test_step_from_value(self):
        # "9/3" in the hour field means hours 9..23 stepping by 3.
        s = parse("* 9/3 * * *")
        self.assertEqual(s.hours, {9, 12, 15, 18, 21})

    def test_range(self):
        s = parse("0 9-17 * * 1-5")
        self.assertEqual(s.hours, set(range(9, 18)))
        self.assertEqual(s.dows, {1, 2, 3, 4, 5})

    def test_named_month(self):
        s = parse("0 0 1 JAN *")
        self.assertEqual(s.months, {1})

    def test_named_dow(self):
        s = parse("0 0 * * MON")
        self.assertEqual(s.dows, {1})

    def test_sunday_seven_aliases_zero(self):
        s = parse("0 0 * * 7")
        self.assertEqual(s.dows, {0})

    def test_question_mark_is_star(self):
        s = parse("0 0 ? * ?")
        self.assertTrue(s.dom_is_star)
        self.assertTrue(s.dow_is_star)

    def test_list_union(self):
        s = parse("0,30 0,12 * * *")
        self.assertEqual(s.minutes, {0, 30})
        self.assertEqual(s.hours, {0, 12})


class TestParseInvalid(unittest.TestCase):
    def test_too_many_fields(self):
        with self.assertRaises(CairnError):
            parse("0 0 * * * *")

    def test_too_few_fields(self):
        with self.assertRaises(CairnError):
            parse("0 0 * *")

    def test_minute_out_of_range(self):
        with self.assertRaises(CairnError):
            parse("60 0 * * *")

    def test_hour_out_of_range(self):
        with self.assertRaises(CairnError):
            parse("0 24 * * *")

    def test_month_out_of_range(self):
        with self.assertRaises(CairnError):
            parse("0 0 1 13 *")

    def test_range_start_gt_end(self):
        with self.assertRaises(CairnError):
            parse("0 10-9 * * *")

    def test_bad_token(self):
        with self.assertRaises(CairnError):
            parse("x 0 * * *")


if __name__ == "__main__":
    unittest.main()
