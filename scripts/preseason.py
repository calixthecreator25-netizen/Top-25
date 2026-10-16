#!/usr/bin/env python3
"""Compute preseason rankings from independently verified, complete inputs.
Input JSON: {season, fbs_teams:[...], fcs_teams:[...], playoff_finish:[...]}.
No fabricated ratings; all 6 talent components required for every team.
"""
import json, sys
from pathlib import Path

WEIGHTS = {
 "returning_talent": .35, "transfers": .20, "recruiting": .15,
 "key_positions": .15, "coaching_continuity": .10, "depth": .05
}
TIERS = {"champion": 0, "runner_up": 1, "semifinal": 2, "quarterfinal": 3, "first_round": 4}

def compute(payload):
    fbs = payload["fbs_teams"]
    fcs = payload["fcs_teams"]
    playoff = payload["playoff_finish"]
    if not fbs or not fcs or len(playoff) != 12:
        raise ValueError("Require both complete division rosters and exactly 12 playoff finish records")
    allteams = fbs + fcs
    ids = [t["id"] for t in allteams]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate team ID")
    for team in allteams:
        vals = team.get("talent")
        if not isinstance(vals, dict) or set(vals) != set(WEIGHTS):
            raise ValueError(f"Missing talent factors: {team['id']}")
        if any(type(v) not in (int,float) or not 0 <= v <= 100 for v in vals.values()):
            raise ValueError(f"Talent factors outside 0-100: {team['id']}")
        if not team.get("source_url") or not team.get("source_checked_at"):
            raise ValueError(f"Missing provenance: {team['id']}")
        team["talent_score"] = round(sum(vals[k]*w for k,w in WEIGHTS.items()), 4)
    fbsids = {t["id"] for t in fbs}
    pids = [p["id"] for p in playoff]
    if len(set(pids)) != 12 or set(pids) - fbsids:
        raise ValueError("Playoff teams must be 12 distinct FBS programs")
    for p in playoff:
        if p.get("finish") not in TIERS or type(p.get("prior_merit")) not in (int,float):
            raise ValueError("Invalid playoff finish or missing prior-year merit")
    if sorted([p["finish"] for p in playoff]).count("champion") != 1 or sorted([p["finish"] for p in playoff]).count("runner_up") != 1:
        raise ValueError("Exactly one champion and runner-up required")
    expected = {"champion":1,"runner_up":1,"semifinal":2,"quarterfinal":4,"first_round":4}
    if any(sum(p["finish"]==k for p in playoff)!=n for k,n in expected.items()):
        raise ValueError("Invalid 12-team playoff advancement distribution")
    sorted_playoff = sorted(playoff, key=lambda p:(TIERS[p["finish"]],-p["prior_merit"],p["id"]))
    lookup = {t["id"]:t for t in fbs}
    locked = [dict(lookup[p["id"]],rank=i,reason="prior_playoff_"+p["finish"]) for i,p in enumerate(sorted_playoff,1)]
    eligible = sorted((t for t in fbs if t["id"] not in pids),key=lambda t:(-t["talent_score"],t["id"]))
    top25 = locked + [dict(t,rank=i,reason="roster_talent") for i,t in enumerate(eligible[:13],13)]
    def talent_order(teams):
        return [dict(t,talent_rank=i) for i,t in enumerate(sorted(teams,key=lambda t:(-t["talent_score"],t["id"])),1)]
    return {"season":payload["season"],"preseason_top25":top25,
            "fbs_talent":talent_order(fbs),"fcs_talent":talent_order(fcs),
}

if __name__=="__main__":
    if len(sys.argv)!=3:
        sys.exit("Usage: python scripts/preseason.py INPUT.json OUTPUT.json")
    payload=json.loads(Path(sys.argv[1]).read_text(encoding="utf8"))
    result=compute(payload)
    Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print("Validated preseason rankings written:",sys.argv[2])
