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
            self.assertEqual(fbs["methodology_version"],"experimental-0.5")
            self.assertEqual(fbs["games_involving_division_i"],1)
            alpha=next(t for t in fbs["teams"] if t["name"]=="Alpha")
            self.assertEqual((alpha["wins"],alpha["losses"],len(alpha["games"])),(1,0,1))
            self.assertEqual(len(fcs["teams"][0]["games"]),0)
            beta=next(t for t in fbs["teams"] if t["name"]=="Beta")
            self.assertEqual(beta["components"]["result_quality"],0)
            self.assertGreater(beta["components"]["schedule_strength"],0)
            c=alpha["components"]
            expected=.5*c["schedule_strength"]+.25*c["result_quality"]+.15*c["win_percentage"]+.1*c["conference_strength"]
            self.assertAlmostEqual(alpha["merit_score"],expected,places=3)

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


    def test_g5_power_conference_upsets_are_rewarded(self):
        """A smaller-conference team's wins over stronger opponents earn result credit."""
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);src=root/"raw";out=root/"out";src.mkdir()
            teams=[
                {"id":1,"school":"Underdog","classification":"fbs","conference":"Small"},
                {"id":2,"school":"Power A","classification":"fbs","conference":"Power"},
                {"id":3,"school":"Power B","classification":"fbs","conference":"Power"},
                {"id":4,"school":"Power C","classification":"fbs","conference":"Power"},
                {"id":5,"school":"Weak","classification":"fbs","conference":"Small"},
                {"id":6,"school":"Weak B","classification":"fbs","conference":"Small"},
                {"id":7,"school":"Weak C","classification":"fbs","conference":"Small"}]
            games=[]
            for game_id,home,away in [(1,1,2),(2,1,3),(3,1,4),
                                       (4,2,5),(5,3,6),(6,4,7),
                                       (7,5,6),(8,5,7)]:
                games.append({"id":game_id,"homeId":home,"awayId":away,
                              "homeTeam":teams[home-1]["school"],"awayTeam":teams[away-1]["school"],
                              "homePoints":21,"awayPoints":7,"completed":True,"startDate":"2026-10-01"})
            for name,records in [("all_teams",teams),("fbs_games",games),("fcs_games",games)]:
                (src/(name+"_2026.json")).write_text(json.dumps({"records":records}))
            run(src,out,2026,"2026-10-15")
            rows=json.loads((out/"fbs.json").read_text())["teams"]
            underdog=next(t for t in rows if t["name"]=="Underdog")
            self.assertEqual((underdog["wins"],underdog["losses"]),(3,0))
            self.assertGreater(underdog["components"]["result_quality"],0)
            self.assertEqual(underdog["rank"],1)

    def test_conference_strength_uses_results_not_conference_name(self):
        """Changing only the names of conferences must not change merit scores."""
        def compute(names):
            with tempfile.TemporaryDirectory() as temp:
                root=Path(temp);src=root/"raw";out=root/"out";src.mkdir()
                teams=[{"id":i,"school":f"Team {i}","classification":"fbs",
                        "conference":names[0] if i in (1,2) else names[1]} for i in range(1,5)]
                games=[{"id":i,"homeId":home,"awayId":away,
                        "homeTeam":f"Team {home}","awayTeam":f"Team {away}",
                        "homePoints":21,"awayPoints":7,"completed":True,"startDate":"2026-10-01"}
                       for i,(home,away) in enumerate([(1,3),(2,4),(3,2)],1)]
                for name,records in [("all_teams",teams),("fbs_games",games),("fcs_games",games)]:
                    (src/(name+"_2026.json")).write_text(json.dumps({"records":records}))
                run(src,out,2026,"2026-10-15")
                return {t["id"]:t["merit_score"] for t in json.loads((out/"fbs.json").read_text())["teams"]}
        self.assertEqual(compute(("SEC","Sun Belt")),compute(("Sun Belt","SEC")))

if __name__=="__main__":
    unittest.main()
