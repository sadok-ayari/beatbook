import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from beatbook import cli


class CliTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.articles = os.path.join(os.path.dirname(__file__), "fixtures", "articles.json")
        self.config = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "themes.json")
        self.out = os.path.join(self.dir.name, "out")
        self.db = os.path.join(self.dir.name, "b.db")

    def tearDown(self):
        self.dir.cleanup()

    def run_cli(self, *args):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = cli.main(list(args))
        return code, buffer.getvalue()

    def test_run_reports_journalists_and_byline_rate(self):
        code, out = self.run_cli("run", "--articles", self.articles, "--config", self.config,
                                 "--out", self.out, "--db", self.db, "--day", "2026-11-12", "--json")
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["pieces"], 6)
        self.assertEqual(payload["with_byline"], 5)
        self.assertIn("Aisha Karim", payload["journalists"])
        self.assertTrue(os.path.exists(os.path.join(self.out, "beatbook.md")))

    def test_show_finds_a_journalist(self):
        self.run_cli("run", "--articles", self.articles, "--config", self.config,
                     "--out", self.out, "--db", self.db)
        code, out = self.run_cli("show", "aisha", "--db", self.db)
        self.assertEqual(code, 0)
        self.assertIn("Aisha Karim", out)
        self.assertIn("3 pieces", out)

    def test_show_unknown_exits_one(self):
        self.run_cli("run", "--articles", self.articles, "--config", self.config,
                     "--out", self.out, "--db", self.db)
        code, _ = self.run_cli("show", "nobody", "--db", self.db)
        self.assertEqual(code, 1)

    def test_missing_articles_exits_two(self):
        code, _ = self.run_cli("run", "--articles", os.path.join(self.dir.name, "x.json"),
                               "--config", self.config, "--db", self.db)
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
