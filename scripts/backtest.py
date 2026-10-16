"""Retrospective rolling-origin test: use rankings before each game to predict its winner."""
import argparse,collections,datetime,json,tempfile
from pathlib import Path
try:
 from scripts.experimental_rankings import run
except ModuleNotFoundError:
 from experimental_rankings import run

def backtest(source,season,output,start_week=4,weights=(.4,.3,.2,.1)):
 source=Path(source);output=Path(output)
 games={}
 for division in ("fbs","fcs"):
  for g in json.loads((source/f"{division}_games_{season}.json").read_text())["records"]:
   games[str(g["id"])]=g
 played=[g for g in games.values() if g.get("completed") is True and g.get("startDate") and g.get("homePoints") is not None and g.get("awayPoints") is not None]
 if not played:raise ValueError("No completed games for backtesting")
 dates=sorted({g["startDate"][:10] for g in played})
 first=datetime.date.fromisoformat(dates[0])
 last=datetime.date.fromisoformat(dates[-1])
 # Every cutoff is Sunday: training games through cutoff, evaluate following Monday-Sunday.
 cutoff=first+datetime.timedelta(days=(6-first.weekday())%7)
 observations=[];weeks=[]
 with tempfile.TemporaryDirectory() as tmp:
  out=Path(tmp)
  while cutoff<last:
   evaluation_end=cutoff+datetime.timedelta(days=7)
   if (cutoff-first).days>=7*start_week:
    run(source,out,season,cutoff.isoformat())
    ratings={}
    for division in ("fbs","fcs"):
     for t in json.loads((out/(division+".json")).read_text())["teams"]:
      ratings[t["id"]]={"score":sum(w*t["components"][k] for w,k in zip(weights,("schedule_strength","result_quality","win_percentage","conference_strength"))),"games":t["wins"]+t["losses"]+t.get("ties",0),"win_rate":(t["wins"]+.5*t.get("ties",0))/max(1,t["wins"]+t["losses"]+t.get("ties",0))}
    weekly=[]
    for g in played:
     d=datetime.date.fromisoformat(g["startDate"][:10])
     if not cutoff<d<=evaluation_end:continue
     a,b=str(g.get("homeId")),str(g.get("awayId"))
     if a not in ratings or b not in ratings:continue
     if ratings[a]["games"]<2 or ratings[b]["games"]<2:continue
     if g["homePoints"]==g["awayPoints"]:continue
     margin=ratings[a]["score"]-ratings[b]["score"]
     if abs(margin)<1e-8:continue
     actual_home=g["homePoints"]>g["awayPoints"]
     predicted_home=margin>0
     weekly.append({"date":d.isoformat(),"home":g.get("homeTeam"),"away":g.get("awayTeam"),"correct":predicted_home==actual_home,"predicted":g.get("homeTeam") if predicted_home else g.get("awayTeam"),"winner":g.get("homeTeam") if actual_home else g.get("awayTeam"),"score_gap":round(abs(margin),3),"home_correct":actual_home,"record_correct":(ratings[a]["win_rate"]>=ratings[b]["win_rate"])==actual_home})
    observations.extend(weekly)
    weeks.append({"cutoff":cutoff.isoformat(),"games":len(weekly),"correct":sum(x["correct"] for x in weekly)})
   cutoff+=datetime.timedelta(days=7)
 if not observations:raise ValueError("No eligible out-of-sample games; cannot report validation")
 correct=sum(x["correct"] for x in observations)
 baseline_home=sum(x["home_correct"] for x in observations)
 baseline_record=sum(x["record_correct"] for x in observations)
 report={"season":season,"weights":list(weights),"status":"RETROSPECTIVE_EXPERIMENTAL","methodology":"For each Sunday cutoff, recompute ratings from completed games through that date and predict winners of the next seven days. Exclude ties, score ties and teams with fewer than two previous games. No home-field adjustment.","limitations":["Historical team and conference memberships come from the available team endpoint, which may not be season-specific.","Game results are historical; no actual betting market or official poll benchmark is used.","Win prediction accuracy alone does not prove ranking fairness or postseason selection quality.","This test does not establish unbiased conference-strength estimates."],"evaluated_games":len(observations),"correct_predictions":correct,"accuracy":round(correct/len(observations),4),"benchmarks":{"always_home":{"correct":baseline_home,"accuracy":round(baseline_home/len(observations),4)},"prior_win_percentage":{"correct":baseline_record,"accuracy":round(baseline_record/len(observations),4),"tie_break":"home"}},"weeks":weeks,"examples":observations[:30]}
 output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2))
 print("Backtest",season,correct,"/",len(observations),"=",report["accuracy"])
 print("Benchmarks: home",baseline_home,"/",len(observations),"prior W-L",baseline_record,"/",len(observations))
 return report
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--season",type=int,required=True);p.add_argument("--output",required=True);p.add_argument("--start-week",type=int,default=4);p.add_argument("--weights",type=float,nargs=4,default=[.4,.3,.2,.1])
 a=p.parse_args();assert all(x>=0 for x in a.weights) and abs(sum(a.weights)-1)<1e-8,"Weights must be nonnegative and total 1"
 backtest(a.source,a.season,a.output,a.start_week,a.weights)
