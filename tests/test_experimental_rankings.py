"""Regression tests for experimental data integrity and duplicate game IDs."""
import json
import tempfile
import unittest
from pathlib import Path
from scripts.experimental_rankings import run

class ExperimentalRankingsTests(unittest.TestCase):
    def test_duplicate_games_and_cross_division_results(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);src=root/"raw";out=root/"out";src.mkdir()
            teams=[
              {"id":1,"school":"Alpha","classification":"fbs","conference":"A"},
              {"id":2,"school":"Beta","classification":"fbs","conference":"B"},
              {"id":3,"school":"Gamma","classification":"fcs","conference":"C"}]
            game={"id":10,"homeId":1,"awayId":2,"homeTeam":"Alpha","awayTeam":"Beta",
                  "homePoints":14,"awayPoints":7,"completed":True,"startDate":"2026-09-01T12:00:00Z"}
            future={"id":11,"homeId":1,"awayId":3,"homeTeam":"Alpha","awayTeam":"Gamma",
                    "homePoints":None,"awayPoints":None,"completed":False,"startDate":"2026-11-01T12:00:00Z"}
            for name,records in [("all_teams",teams),("fbs_games",[game,future]),("fcs_games",[game,future])]:
                (src/(name+"_2026.json")).write_text(json.dumps({"records":records}))
            run(src,out,2026,"2026-10-15")
            fbs=json.loads((out/"fbs.json").read_text())
            fcs=json.loads((out/"fcs.json").read_text())
            self.assertEqual(len(fbs["teams"]),2)
            self.assertEqual(len(fcs["teams"]),1)
            self.assertEqual(fbs["games_involving_division_i"],1)
            alpha=next(t for t in fbs["teams"] if t["name"]=="Alpha")
            self.assertEqual((alpha["wins"],alpha["losses"],len(alpha["games"])),(1,0,1))
            self.assertEqual(len(fcs["teams"][0]["games"]),0)
            beta=next(t for t in fbs["teams"] if t["name"]=="Beta")
            self.assertEqual(beta["components"]["result_quality"],0)
            self.assertGreater(beta["components"]["schedule_strength"],0)

    def test_unplayed_team_does_not_outrank_team_with_results(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);src=root/"raw";out=root/"out";src.mkdir()
            teams=[
                {"id":1,"school":"Winner","classification":"fbs","conference":"A"},
                {"id":2,"school":"Loser","classification":"fbs","conference":"B"},
                {"id":3,"school":"Idle","classification":"fbs","conference":"C"},
                {"id":4,"school":"FCS","classification":"fcs","conference":"D"}]
            game={"id":1,"homeId":1,"awayId":2,"homeTeam":"Winner","awayTeam":"Loser",
                  "homePoints":21,"awayPoints":14,"completed":True,"startDate":"2026-10-01"}
            for name,records in [("all_teams",teams),("fbs_games",[game]),("fcs_games",[game])]:
                (src/(name+"_2026.json")).write_text(json.dumps({"records":records}))
            run(src,out,2026,"2026-10-15")
            rows=json.loads((out/"fbs.json").read_text())["teams"]
            self.assertEqual(rows[-1]["name"],"Idle")
            self.assertEqual(len(rows),3)

if __name__=="__main__":
    unittest.main()
