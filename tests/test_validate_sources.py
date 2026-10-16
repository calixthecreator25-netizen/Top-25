import json
import tempfile
import unittest
from pathlib import Path
from scripts.validate_sources import validate

class SourceValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.teams=[{"id":1,"school":"Alpha","classification":"fbs"},{"id":2,"school":"Beta","classification":"fcs"}]
        self.game={"id":10,"homeId":1,"awayId":2,"startDate":"2026-09-01",
                   "completed":True,"homePoints":21,"awayPoints":7}
        self.write("all_teams",self.teams)
        self.write("fbs_teams",[self.teams[0]])
        self.write("fbs_games",[self.game])
        self.write("fcs_games",[self.game])
    def write(self,name,records):
        (self.root/f"{name}_2026.json").write_text(json.dumps({"season":2026,"records":records}))
    def check(self):
        return validate(self.root,self.root/"audit.json",2026)
    def test_valid_duplicate_across_divisions(self):
        result=self.check()
        self.assertEqual(result["status"],"PASS")
        self.assertEqual(result["duplicate_records"],1)
        self.assertEqual(result["completed_games"],1)
    def test_conflicting_game_rejected(self):
        changed=dict(self.game,homePoints=35)
        self.write("fcs_games",[changed])
        with self.assertRaisesRegex(ValueError,"Conflicting duplicate"):
            self.check()
    def test_invalid_score_rejected(self):
        bad=dict(self.game,awayPoints=-3)
        self.write("fbs_games",[bad]);self.write("fcs_games",[bad])
        with self.assertRaisesRegex(ValueError,"invalid scores"):
            self.check()
    def test_missing_fbs_team_rejected(self):
        self.write("fbs_teams",[{"id":99,"school":"Missing"}])
        with self.assertRaisesRegex(ValueError,"missing from all_teams"):
            self.check()
