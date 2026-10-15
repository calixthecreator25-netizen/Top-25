#!/usr/bin/env python3
"""Validate official merit ranking JSON. Missing or invented data must not publish."""
import json, sys
from pathlib import Path

REQUIRED = {"season", "division", "as_of", "methodology_version", "teams"}
DIVISIONS = {"FBS", "FCS"}
COMPONENTS = {"schedule_strength", "result_quality", "win_percentage", "conference_strength"}
WEIGHTS = {"schedule_strength": .40, "result_quality": .30, "win_percentage": .20, "conference_strength": .10}

def validate(data):
    errors = []
    if not isinstance(data, dict):
        return ["Root must be an object"]
    missing = REQUIRED - data.keys()
    if missing:
        return [f"Missing root fields: {sorted(missing)}"]
    if data["division"] not in DIVISIONS:
        errors.append("Invalid division")
    if not isinstance(data["season"], int) or data["season"] < 1900:
        errors.append("Invalid season")
    if not isinstance(data["teams"], list) or not data["teams"]:
        return errors + ["Teams must be a nonempty list"]
    ids, ranks = set(), set()
    for i, t in enumerate(data["teams"]):
        if not isinstance(t, dict):
            errors.append(f"Team {i} must be an object"); continue
        name = t.get("name", f"row {i}")
        tid = t.get("id")
        rank = t.get("rank")
        if not isinstance(tid, str) or not tid.strip() or tid in ids:
            errors.append(f"{name}: missing/duplicate id")
        ids.add(tid)
        if not isinstance(rank, int) or isinstance(rank, bool) or rank < 1 or rank in ranks:
            errors.append(f"{name}: invalid/duplicate rank")
        ranks.add(rank)
        for field in ("wins", "losses"):
            val = t.get(field)
            if not isinstance(val, int) or isinstance(val, bool) or val < 0:
                errors.append(f"{name}: invalid {field}")
        scores = t.get("components")
        if not isinstance(scores, dict) or set(scores) != COMPONENTS:
            errors.append(f"{name}: missing/unexpected score components"); continue
        if any(not isinstance(v, (int,float)) or isinstance(v,bool) or not 0 <= v <= 100 for v in scores.values()):
            errors.append(f"{name}: component outside 0–100"); continue
        expected = sum(scores[k]*WEIGHTS[k] for k in WEIGHTS)
        score = t.get("merit_score")
        if not isinstance(score, (int,float)) or isinstance(score,bool) or abs(score-expected) > .011:
            errors.append(f"{name}: merit_score does not match weighted formula")
        if not t.get("source_url") or not t.get("source_checked_at"):
            errors.append(f"{name}: missing source provenance")
    if ranks != set(range(1, len(data["teams"])+1)):
        errors.append("Ranks must be contiguous from 1")
    return errors

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: validate_rankings.py path/to/rankings.json")
    path = Path(sys.argv[1])
    issues = validate(json.loads(path.read_text(encoding="utf-8")))
    if issues:
        print("\n".join(issues)); sys.exit(1)
    print(f"PASS: {path}")
