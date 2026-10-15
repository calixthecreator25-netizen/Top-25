"""Build transparent, dated conference standings from completed games and CFBD team records."""
import argparse,collections,json
from pathlib import Path

def build(raw,rankings,output,season):
 raw,rankings,output=Path(raw),Path(rankings),Path(output)
 teams=json.loads((raw/f"all_teams_{season}.json").read_text())["records"]
 games={}
 for div in ("fbs","fcs"):
  for g in json.loads((raw/f"{div}_games_{season}.json").read_text())["records"]:
   games[g["id"]]=g
 by_id={str(t["id"]):t for t in teams if str(t.get("classification","")).upper() in ("FBS","FCS")}
 output.mkdir(parents=True,exist_ok=True)
 for division in ("fbs","fcs"):
  poll=json.loads((rankings/(division+".json")).read_text())
  as_of=poll["as_of"]
  ranked={t["id"]:t for t in poll["teams"]}
  records=collections.defaultdict(lambda:{"wins":0,"losses":0,"ties":0})
  for g in games.values():
   if not g.get("completed") or not g.get("startDate") or g["startDate"][:10]>as_of:continue
   a,b=str(g.get("homeId")),str(g.get("awayId"))
   if a not in by_id or b not in by_id:continue
   home,away=by_id[a],by_id[b]
   if str(home["classification"]).lower()!=division or str(away["classification"]).lower()!=division:continue
   if not home.get("conference") or home.get("conference")!=away.get("conference"):continue
   hp,ap=g.get("homePoints"),g.get("awayPoints")
   if hp is None or ap is None:continue
   if hp>ap:records[a]["wins"]+=1;records[b]["losses"]+=1
   elif hp<ap:records[b]["wins"]+=1;records[a]["losses"]+=1
   else:records[a]["ties"]+=1;records[b]["ties"]+=1
  conferences=collections.defaultdict(list)
  for t in poll["teams"]:
   rec=records[t["id"]]
   conferences[t["conference"]].append({"id":t["id"],"name":t["name"],"rank":t["rank"],"overall_wins":t["wins"],"overall_losses":t["losses"],"conference_wins":rec["wins"],"conference_losses":rec["losses"],"conference_ties":rec["ties"],"merit_score":t["merit_score"]})
  for rows in conferences.values():
   rows.sort(key=lambda t:(-(t["conference_wins"]+.5*t["conference_ties"])/max(1,t["conference_wins"]+t["conference_losses"]+t["conference_ties"]),-t["conference_wins"],t["conference_losses"],t["rank"],t["name"]))
  payload={"division":division.upper(),"as_of":as_of,"status":"EXPERIMENTAL_NOT_OFFICIAL","note":"Conference records reflect completed same-conference games. Equal records are displayed in merit-rank order for convenience, not as an official conference tiebreaker.","conferences":[{"name":name,"teams":rows} for name,rows in sorted(conferences.items())]}
  (output/(division+".json")).write_text(json.dumps(payload,separators=(",",":")))
  print(division,len(conferences),"conferences")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--raw",default="data/raw");p.add_argument("--rankings",default="data/experimental");p.add_argument("--output",default="data/conferences");p.add_argument("--season",type=int,default=2026)
 a=p.parse_args();build(a.raw,a.rankings,a.output,a.season)
