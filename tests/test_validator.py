import unittest
from scripts.validate_rankings import validate

class RankingValidatorTests(unittest.TestCase):
    def setUp(self):
        self.data = {
            "season": 2026, "division": "FBS", "as_of": "2026-10-15",
            "methodology_version": "draft-1.1",
            "teams": [{
                "id": "example", "name": "Example University", "rank": 1,
                "wins": 1, "losses": 0,
                "components": {"schedule_strength": 50, "result_quality": 60,
                               "win_percentage": 100, "conference_strength": 40},
                "merit_score": 62.0,
                "source_url": "https://example.org/game-results",
                "source_checked_at": "2026-10-15"
            }]
        }
    def test_valid(self):
        self.assertEqual(validate(self.data), [])
    def test_missing_provenance(self):
        del self.data["teams"][0]["source_url"]
        self.assertTrue(validate(self.data))
    def test_incorrect_score(self):
        self.data["teams"][0]["merit_score"] = 99
        self.assertTrue(validate(self.data))
    def test_duplicate_rank(self):
        self.data["teams"].append(dict(self.data["teams"][0], id="other"))
        self.assertTrue(validate(self.data))

if __name__ == "__main__":
    unittest.main()
