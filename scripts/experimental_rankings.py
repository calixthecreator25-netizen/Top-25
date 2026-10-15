"""Experimental results-only Division I ranking calculator. Not official."""
import argparse, collections, datetime, json
from pathlib import Path

def run(src, dest, season, as_of):
    src, dest = Path(src), Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    def read(name):
        return json.loads((src / f"{name}_{season}.json").read_text())["records"]
    teams = {t["id"]:t for t in read("all_teams") if str(t.get("classification","")).lower() in ("fbs","fcs")}
    games = {g["id"]:g for g in read("fbs_games")+read("fcs_games")}
    if not teams or not games:
        raise ValueError("Missing Division I teams or game schedule; refusing to publish empty rankings")
    valid = [g for g in games.values() if g.get("completed") is True
             and g.get("startDate") and g["startDate"][:10] <= as_of
             and g.get("homePoints") is not None and g.get("awayPoints") is not None
             and (g.get("homeId") in teams or g.get("awayId") in teams)]
    d1 = [g for g in valid if g["homeId"] in teams and g["awayId"] in teams]
    rating = {i:.5 for i in teams}
    for _ in range(75):
        results=collections.defaultdict(list)
        for g in d1:
            a,b=g["homeId"],g["awayId"]
            w=1 if g["homePoints"]>g["awayPoints"] else 0 if g["homePoints"]<g["awayPoints"] else .5
            results[a].append((w,rating[b]))
            results[b].append((1-w,rating[a]))
        nxt={}
        for i in teams:
            r=results[i]; n=len(r)
            avg=sum((w+opp)/2 for w,opp in r)/n if n else .5
            nxt[i]=max(0,min(1,(n*avg+1)/(n+2)))
        rating=nxt
    records=collections.defaultdict(list)
    conf_results=collections.defaultdict(list)
    for g in valid:
        for side,other in (("home","away"),("away","home")):
            i=g[side+"Id"]; opp=g[other+"Id"]
            if i not in teams: continue
            own,against=g[side+"Points"],g[other+"Points"]
            result="W" if own>against else "L" if own<against else "T"
            records[i].append({"opponent":teams[opp]["school"] if opp in teams else g[other+"Team"],
                "date":g["startDate"][:10],"result":result,"score":f"{own}-{against}",
                "opponent_rating":round(rating[opp]*100,2) if opp in teams else None})
            if opp in teams:
                a,b=teams[i],teams[opp]
                if (a.get("conference"),a["classification"])!=(b.get("conference"),b["classification"]):
                    conf_results[(a["classification"],a.get("conference"))].append((1 if result=="W" else 0 if result=="L" else .5,rating[opp]))
    conf={}
    for key,rs in conf_results.items():
        conf[key]=100*(sum((w+opp)/2 for w,opp in rs)+2.5)/(len(rs)+5)
    for division in ("FBS","FCS"):
        rows=[]
        for i,t in teams.items():
            if str(t["classification"]).upper()!=division: continue
            gs=records[i]; n=len(gs)
            wins=sum(g["result"]=="W" for g in gs)
            losses=sum(g["result"]=="L" for g in gs)
            ties=n-wins-losses
            relevant=[g for g in gs if g["opponent_rating"] is not None]
            sos=sum(g["opponent_rating"] for g in relevant)/len(relevant) if relevant else 50
            quality=sum((100 if g["result"]=="W" else 50 if g["result"]=="T" else 0)*.5+g["opponent_rating"]*.5 for g in relevant)/len(relevant) if relevant else 50
            wpct=100*(wins+.5*ties)/n if n else 50
            conference=conf.get((t["classification"],t.get("conference")),50)
            components={"schedule_strength":round(sos,4),"result_quality":round(quality,4),
                        "win_percentage":round(wpct,4),"conference_strength":round(conference,4)}
            score=.4*sos+.3*quality+.2*wpct+.1*conference
            rows.append({"id":str(i),"name":t["school"],"conference":t.get("conference") or "Independent",
                "wins":wins,"losses":losses,"ties":ties,"merit_score":round(score,4),
                "components":components,"games":gs})
        rows.sort(key=lambda t:(t["wins"]+t["losses"]+t["ties"]==0,-t["merit_score"],-t["wins"],t["name"]))
        for j,t in enumerate(rows):
            t["rank"]=j+1
            t["team_above"]=rows[j-1]["name"] if j else None
            t["gap_to_team_above"]=round(rows[j-1]["merit_score"]-t["merit_score"],4) if j else 0
        payload={"season":season,"division":division,"as_of":as_of,
            "status":"EXPERIMENTAL_NOT_OFFICIAL","methodology_version":"experimental-0.2",
            "source":"CollegeFootballData API","games_involving_division_i":len(valid),
            "notes":["Unvalidated opponent/conference model","No subjective prestige or scoring margin",
                     "Teams without completed games placed below teams with results; not official rankings"],
            "teams":rows}
        (dest/f"{division.lower()}.json").write_text(json.dumps(payload,separators=(",",":")))
        print(division,len(rows),"ranked teams; leader:",rows[0]["name"])
    print("Completed relevant games",len(valid),"Division I vs Division I",len(d1))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True);p.add_argument("--output",required=True)
    p.add_argument("--season",type=int,default=2026)
    p.add_argument("--as-of",default=datetime.datetime.now(datetime.timezone.utc).date().isoformat())
    a=p.parse_args();run(a.source,a.output,a.season,a.as_of)
