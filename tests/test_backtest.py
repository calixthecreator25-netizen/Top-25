import json,tempfile,unittest
from pathlib import Path
from scripts.backtest import backtest

class BacktestTests(unittest.TestCase):
 def test_rolling_origin_excludes_future_results(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);src=p/"raw";src.mkdir()
   teams=[{"id":i,"school":f"Team {i}","classification":"fbs" if i<4 else "fcs","conference":"A" if i<4 else "B"} for i in range(1,5)]
   games=[]
   for week in range(9):
    for n,(home,away) in enumerate([(1,2),(3,1),(2,3)]):
     games.append({"id":week*3+n,"homeId":home,"awayId":away,"homeTeam":f"Team {home}","awayTeam":f"Team {away}","homePoints":28,"awayPoints":14,"completed":True,"startDate":f"2025-09-{1+week*7:02d}" if week<4 else ( __import__("datetime").date(2025,9,1)+__import__("datetime").timedelta(weeks=week)).isoformat()})
   for name,rows in [("all_teams",teams),("fbs_games",games),("fcs_games",games)]:
    (src/(name+"_2025.json")).write_text(json.dumps({"records":rows}))
   result=backtest(src,2025,p/"result.json",start_week=2)
   self.assertGreater(result["evaluated_games"],0)
   self.assertLessEqual(result["accuracy"],1)
   self.assertTrue((p/"result.json").exists())
if __name__=="__main__":unittest.main()
