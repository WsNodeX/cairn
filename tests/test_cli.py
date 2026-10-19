import io
import unittest
from contextlib import redirect_stdout

from cairn.cli import main


class TestCLI(unittest.TestCase):
    def _run(self, argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(argv)
        return rc, buf.getvalue().strip().splitlines()

    def test_next_first_of_month(self):
        rc, lines = self._run(
            ["next", "0 0 1 * *", "-n", "2", "-f", "2026-10-19T14:00:00"]
        )
        self.assertEqual(rc, 0)
        self.assertEqual(
            lines, ["2026-11-01T00:00:00", "2026-12-01T00:00:00"]
        )

    def test_prev_first_of_month(self):
        rc, lines = self._run(
            ["prev", "0 0 1 * *", "-f", "2026-10-19T14:00:00"]
        )
        self.assertEqual(rc, 0)
        self.assertEqual(lines, ["2026-10-01T00:00:00"])

    def test_invalid_expression_returns_2(self):
        rc, _ = self._run(["next", "60 0 1 * *"])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
