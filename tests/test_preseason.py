import unittest
from scripts.preseason import compute, WEIGHTS

def team(i):
    return {"id":i,"name":i,"talent":{k:70 for k in WEIGHTS},
            "source_url":"https://example.org/verified","source_checked_at":"2026-08-01"}

class PreseasonTests(unittest.TestCase):
    def setUp(self):
        self.payload={"season":2026,
                      "fbs_teams":[team(f"fbs{i}") for i in range(25)],
                      "fcs_teams":[team("fcs1")],
                      "playoff_finish":[
                          {"id":f"fbs{i}","finish":finish,"prior_merit":100-i}
                          for i,finish in enumerate(["champion","runner_up"]+["semifinal"]*2+["quarterfinal"]*4+["first_round"]*4)]}
    def test_preseason_top25(self):
        r=compute(self.payload)
        self.assertEqual(len(r["preseason_top25"]),25)
        self.assertEqual(r["preseason_top25"][0]["reason"],"prior_playoff_champion")
        self.assertEqual(r["preseason_top25"][11]["reason"],"prior_playoff_first_round")
        self.assertEqual(r["preseason_top25"][12]["reason"],"roster_talent")
    def test_non_playoff_team_starts_after_playoff_twelve(self):
        self.payload["fbs_teams"][24]["talent"]={k:100 for k in WEIGHTS}
        r=compute(self.payload)
        self.assertEqual(r["preseason_top25"][12]["id"],"fbs24")
        self.assertEqual(r["preseason_top25"][0]["id"],"fbs0")
    def test_missing_talent_rejected(self):
        del self.payload["fcs_teams"][0]["talent"]["depth"]
        with self.assertRaises(ValueError):compute(self.payload)
    def test_missing_provenance_rejected(self):
        del self.payload["fbs_teams"][0]["source_url"]
        with self.assertRaises(ValueError):compute(self.payload)
    def test_invalid_playoff_rejected(self):
        self.payload["playoff_finish"][2]["finish"]="champion"
        with self.assertRaises(ValueError):compute(self.payload)

if __name__=="__main__":unittest.main()
