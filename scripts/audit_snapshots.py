#!/usr/bin/env python3
"""Audit downloaded CFBD source snapshot files without publishing rankings."""
import json
import sys
from pathlib import Path

def read(path):
    with open(path, encoding="utf-8") as f:
        data=json.load(f)
    if not isinstance(data.get("records"), list):
        raise ValueError(f"{path} missing records list")
    return data["records"]

def audit(folder,season):
    fbs=read(folder/f"fbs_teams_{season}.json")
    teams=read(folder/f"all_teams_{season}.json")
    fbs_games=read(folder/f"fbs_games_{season}.json")
    fcs_games=read(folder/f"fcs_games_{season}.json")
    fbsids={t["id"] for t in fbs}
    fcsids={t["id"] for t in teams if (t.get("classification") or "").lower()=="fcs"}
    ids1={g["id"] for g in fbs_games}
    ids2={g["id"] for g in fcs_games}
    unique={g["id"]:g for g in fbs_games+fcs_games}
    eligible=[g for g in unique.values() if g.get("homeId") in fbsids|fcsids or g.get("awayId") in fbsids|fcsids]
    completed=[g for g in eligible if g.get("completed") is True and g.get("homePoints") is not None and g.get("awayPoints") is not None]
    report={
      "season":season,"fbs_team_count":len(fbsids),"cfbd_fcs_classified_count":len(fcsids),
      "all_teams_returned":len(teams),"fbs_query_game_count":len(fbs_games),
      "fcs_query_game_count":len(fcs_games),
      "game_id_overlap_between_queries":len(ids1&ids2),
      "unique_game_count":len(unique),"division_i_involved_game_count":len(eligible),
      "completed_division_i_involved_games_with_scores":len(completed),
      "warnings":[]
    }
    if ids1==ids2:report["warnings"].append("Both game requests returned identical game IDs; do not count them twice.")
    if len(fcsids)==0:report["warnings"].append("No FCS classifications found; verify source structure.")
    report["warnings"].append("CFBD membership labels require independent NCAA season-specific reconciliation.")
    report["warnings"].append("This is an input audit, not an official ranking calculation.")
    return report

if __name__=="__main__":
    if len(sys.argv)!=3:sys.exit("Usage: python scripts/audit_snapshots.py FOLDER YEAR")
    print(json.dumps(audit(Path(sys.argv[1]),int(sys.argv[2])),indent=2))
