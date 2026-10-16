import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from scripts.publication_gate import first_merit_date, may_publish

class PublicationGateTests(unittest.TestCase):
    def test_four_full_weeks_then_monday(self):
        self.assertEqual(first_merit_date(dt.date(2026, 8, 29)), dt.date(2026, 9, 28))
    def test_monday_threshold(self):
        self.assertEqual(first_merit_date(dt.date(2026, 8, 24)), dt.date(2026, 9, 21))
    def test_gate_prevents_early_publication_and_wrong_season(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            games = {"records":[{"seasonType":"regular","startDate":"2026-08-29T12:00:00Z"}]}
            for div in ("fbs","fcs"):
                (root / f"{div}_games_2026.json").write_text(json.dumps(games))
            self.assertFalse(may_publish(root, 2026, dt.date(2026, 9, 21))[0])
            self.assertTrue(may_publish(root, 2026, dt.date(2026, 9, 28))[0])
            self.assertFalse(may_publish(root, 2026, dt.date(2027, 9, 28))[0])
    def test_no_data_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            for div in ("fbs","fcs"):
                (Path(directory)/f"{div}_games_2026.json").write_text('{"records":[]}')
            with self.assertRaises(ValueError):
                may_publish(directory, 2026, dt.date(2026, 10, 1))
