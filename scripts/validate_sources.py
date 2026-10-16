"""Fail-closed coverage and game-consistency checks for ranking source snapshots."""
import argparse
import json
from pathlib import Path

def validate(source, output, season):
    source = Path(source)
    def records(name):
        payload = json.loads((source / f"{name}_{season}.json").read_text())
        if payload.get("season") not in (None, season):
            raise ValueError(f"{name}: unexpected season")
        return payload["records"]
    all_teams = records("all_teams")
    fbs_teams = records("fbs_teams")
    fbs_games = records("fbs_games")
    fcs_games = records("fcs_games")
    teams = {}
    for t in all_teams:
        if t.get("id") is None:
            continue
        key = str(t["id"])
        if key in teams and teams[key].get("school") != t.get("school"):
            raise ValueError(f"Conflicting team id {key}")
        teams[key] = t
    fbs_ids = {str(t["id"]) for t in fbs_teams if t.get("id") is not None}
    missing = sorted(fbs_ids - set(teams))
    if missing:
        raise ValueError(f"{len(missing)} FBS team IDs missing from all_teams: {missing[:10]}")
    divisions = {div: [t for t in teams.values() if str(t.get("classification","")).lower()==div] for div in ("fbs","fcs")}
    if not all(divisions.values()):
        raise ValueError("Missing FBS or FCS team membership; cannot publish")
    by_game = {}
    conflicts = []
    for g in fbs_games + fcs_games:
        key = str(g.get("id"))
        if key == "None":
            raise ValueError("Game missing ID")
        if key in by_game:
            prior = by_game[key]
            fields = ("homeId","awayId","startDate","completed","homePoints","awayPoints")
            if any(prior.get(f) != g.get(f) for f in fields):
                conflicts.append(key)
        else:
            by_game[key] = g
    if conflicts:
        raise ValueError(f"Conflicting duplicate game records: {conflicts[:10]}")
    unknown = []
    bad_scores = []
    completed = 0
    for g in by_game.values():
        if g.get("completed") is not True:
            continue
        completed += 1
        home,away = g.get("homeId"),g.get("awayId")
        if home is None or away is None:
            bad_scores.append(g.get("id"));continue
        if str(home) not in teams or str(away) not in teams:
            unknown.append(g.get("id"))
        scores = (g.get("homePoints"),g.get("awayPoints"))
        if any(not isinstance(n,int) or isinstance(n,bool) or n<0 for n in scores):
            bad_scores.append(g.get("id"))
    if bad_scores:
        raise ValueError(f"Completed games with invalid scores or participants: {bad_scores[:10]}")
    if completed == 0:
        raise ValueError("No completed games available; refusing to publish")
    report = {"season":season,"fbs_teams":len(divisions["fbs"]),"fcs_teams":len(divisions["fcs"]),
              "fbs_source_ids":len(fbs_ids),"unique_games":len(by_game),
              "completed_games":completed,"completed_games_with_unmapped_opponents":len(unknown),
              "unmapped_game_ids_sample":unknown[:20],
              "duplicate_records":len(fbs_games)+len(fcs_games)-len(by_game),
              "status":"REVIEW_REQUIRED" if unknown else "PASS"}
    out=Path(output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    # Unknown opponents can be lower-division games. Flag, don't invent ratings.
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",default="data/raw")
    p.add_argument("--output",default="data/quality/source-audit.json")
    p.add_argument("--season",type=int,required=True)
    a=p.parse_args()
    validate(a.source,a.output,a.season)
