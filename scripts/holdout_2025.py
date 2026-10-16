"""Compare frozen baseline and selected candidate on untouched 2025 holdout."""
import json,tempfile
from pathlib import Path
try:
 from scripts.backtest import backtest
except ModuleNotFoundError:
 from backtest import backtest

def main():
 with tempfile.TemporaryDirectory() as tmp:
  base=backtest("data/2025",2025,Path(tmp)/"baseline.json",weights=(.40,.30,.20,.10))
  candidate=backtest("data/2025",2025,Path(tmp)/"candidate.json",weights=(.50,.25,.15,.10))
 assert base["evaluated_games"]==candidate["evaluated_games"],"Different eligible-game counts"
 n=base["evaluated_games"]
 result={"status":"FROZEN_2025_HOLDOUT","selection_seasons":[2023,2024],"holdout_season":2025,"published_formula_unchanged":True,"eligible_games":n,"baseline":{"weights":base["weights"],"correct":base["correct_predictions"],"accuracy":base["accuracy"]},"schedule_emphasis":{"weights":candidate["weights"],"correct":candidate["correct_predictions"],"accuracy":candidate["accuracy"]},"difference_correct":candidate["correct_predictions"]-base["correct_predictions"],"limitations":["Candidate was selected on 2023–2024; 2025 was not used for selection.","Predicting winners is not equivalent to fair rankings.","A single holdout season cannot establish future generalization."]}
 out=Path("results/holdout-2025.json");out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(result,indent=2))
 print("2025 holdout:",json.dumps(result,indent=2))
if __name__=="__main__":main()
