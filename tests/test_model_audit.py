import json,tempfile,unittest
from pathlib import Path
from scripts.model_audit import analyze,html

class ModelAuditTests(unittest.TestCase):
 def test_head_to_head_inversion_and_conference_coverage(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)
   def team(name,rank,wins,losses,games):
    return {"id":str(rank),"name":name,"rank":rank,"wins":wins,"losses":losses,"ties":0,"conference":"A","conference_sample_size":2,"merit_score":50.0,"components":{"schedule_strength":50,"result_quality":50,"win_percentage":50,"conference_strength":50},"games":games}
   winner=team("Winner",2,1,0,[{"opponent":"Leader","result":"W","date":"2026-10-01"}])
   leader=team("Leader",1,0,1,[{"opponent":"Winner","result":"L","date":"2026-10-01"}])
   for div in ("fbs","fcs"):
    (p/(div+".json")).write_text(json.dumps({"as_of":"2026-10-15","teams":[leader,winner]}))
   report=analyze(p)
   self.assertEqual(report["divisions"]["fbs"]["head_to_head_inversions"][0]["winner"],"Winner")
   self.assertEqual(report["divisions"]["fcs"]["conference_evidence"][0]["evidence"],"limited")
   self.assertIn("Head-to-head inversions",html(report))
 def test_score_integrity_flag(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)
   row={"id":"1","name":"A","rank":1,"wins":0,"losses":0,"ties":0,"conference":"A","merit_score":90,"components":{"schedule_strength":50,"result_quality":50,"win_percentage":50,"conference_strength":50},"games":[]}
   for div in ("fbs","fcs"):(p/(div+".json")).write_text(json.dumps({"as_of":"2026-10-15","teams":[row]}))
   self.assertEqual(len(analyze(p)["divisions"]["fbs"]["integrity_issues"]),1)
if __name__=="__main__":unittest.main()
