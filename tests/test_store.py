import json
import os
import tempfile
import unittest

from beatbook import report
from beatbook.models import Piece
from beatbook.store import Store

PIECES = [
    Piece("Green bond framework delayed", "National Daily", "Aisha Karim", "https://x/1",
          "2026-11-11", ["climate finance"], negative=3, positive=0),
    Piece("Climate finance deal reached", "Finance Wire", "Aisha Karim", "https://x/2",
          "2026-11-10", ["climate finance"], negative=0, positive=4),
    Piece("Mangrove restoration stalls", "Coastal Post", "Omar Haddad", "https://x/3",
          "2026-11-08", ["nature and water"], negative=2, positive=0),
    Piece("No byline here", "Global Post", "", "https://x/4", "2026-11-07", ["climate policy"]),
]


def store():
    directory = tempfile.TemporaryDirectory()
    return directory, Store(os.path.join(directory.name, "b.db"))


class StoreTests(unittest.TestCase):
    def test_save_ignores_duplicates(self):
        directory, db = store()
        try:
            self.assertEqual(db.save(PIECES), 4)
            self.assertEqual(db.save(PIECES), 0)
        finally:
            db.close()
            directory.cleanup()

    def test_aggregates_by_author(self):
        directory, db = store()
        try:
            db.save(PIECES)
            people = db.journalists()
            self.assertEqual(sorted(people), ["Aisha Karim", "Omar Haddad"])
            aisha = people["Aisha Karim"]
            self.assertEqual(aisha.pieces, 2)
            self.assertEqual(aisha.first_seen, "2026-11-10")
            self.assertEqual(aisha.last_seen, "2026-11-11")
            self.assertEqual(aisha.negative, 3)
            self.assertEqual(aisha.positive, 4)
            self.assertEqual(aisha.beat, ["climate finance"])
        finally:
            db.close()
            directory.cleanup()

    def test_unnamed_pieces_are_excluded(self):
        directory, db = store()
        try:
            db.save(PIECES)
            self.assertNotIn("", db.journalists())
        finally:
            db.close()
            directory.cleanup()

    def test_theme_matrix(self):
        directory, db = store()
        try:
            db.save(PIECES)
            matrix = db.theme_matrix()
            self.assertEqual(matrix["climate finance"]["Aisha Karim"], 2)
            self.assertNotIn("climate policy", matrix)
        finally:
            db.close()
            directory.cleanup()


class ReportTests(unittest.TestCase):
    def test_render_names_and_warns_on_thin_byline_rate(self):
        directory, db = store()
        try:
            db.save(PIECES)
            markdown = report.render(db.journalists(), db.theme_matrix(), "2026-11-12", 4, 3,
                                     ["climate finance", "nature and water", "climate policy"])
        finally:
            db.close()
            directory.cleanup()
        self.assertIn("3 of 4 pieces carried a usable byline", markdown)
        self.assertIn("Aisha Karim", markdown)
        self.assertIn("Who covers what", markdown)
        self.assertIn("one reporter carries this theme", markdown)

    def test_no_byline_warning_when_coverage_is_good(self):
        directory, db = store()
        try:
            db.save(PIECES)
            markdown = report.render(db.journalists(), db.theme_matrix(), "2026-11-12", 4, 4,
                                     ["climate finance"])
        finally:
            db.close()
            directory.cleanup()
        self.assertNotIn("Half the sample has no byline", markdown)


if __name__ == "__main__":
    unittest.main()
