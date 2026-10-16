"""Evaluate prespecified merit weights on 2023–2024 only; never inspect holdout 2025."""
import argparse,json,tempfile
from pathlib import Path
try:
 from scripts.backtest import backtest
except ModuleNotFoundError:
 from backtest import backtest

CANDIDATES={
 "published_baseline":(.40,.30,.20,.10),
 "schedule_emphasis":(.50,.25,.15,.10),
 "result_emphasis":(.30,.40,.20,.10),
 "record_emphasis":(.30,.25,.35,.10),
 "conference_emphasis":(.35,.30,.20,.15),
 "balanced":(.25,.35,.30,.10),
}
def experiment(data_root,output):
 rows=[]
 with tempfile.TemporaryDirectory() as tmp:
  for name,weights in CANDIDATES.items():
   reports=[backtest(Path(data_root)/str(year),year,Path(tmp)/f"{name}-{year}.json",weights=weights) for year in (2023,2024)]
   correct=sum(r["correct_predictions"] for r in reports)
   games=sum(r["evaluated_games"] for r in reports)
   rows.append({"candidate":name,"weights":list(weights),"correct":correct,"games":games,"accuracy":round(correct/games,5),"seasons":[{"season":r["season"],"correct":r["correct_predictions"],"games":r["evaluated_games"]} for r in reports]})
 rows.sort(key=lambda x:(-x["accuracy"],x["candidate"]))
 result={"status":"EXPERIMENTAL_DEVELOPMENT_ONLY","development_seasons":[2023,2024],"holdout_season":2025,"warning":"Selection on development accuracy is exploratory; do not claim out-of-sample improvement until a single frozen candidate is evaluated on the untouched 2025 holdout. Published ranking weights remain unchanged.","candidates":rows}
 output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2))
 print("Development leaderboard:",[(x["candidate"],x["accuracy"]) for x in rows])
 return result
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--data-root",required=True);p.add_argument("--output",required=True)
 a=p.parse_args();experiment(a.data_root,a.output)
