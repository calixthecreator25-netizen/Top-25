"""Compare v0.5 and v0.6 rankings without altering the published poll."""
import argparse, json
from pathlib import Path
from collections import defaultdict
try:
    from scripts.experimental_rankings import run
except ModuleNotFoundError:
    from experimental_rankings import run

def compare(source, output, season, as_of):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    report = {"season": season, "as_of": as_of, "status": "EXPERIMENTAL_REVIEW", "divisions": {}}
    for version, folder in (("experimental-0.5", "v05"), ("experimental-0.6", "v06")):
        run(source, output / folder, season, as_of, version)
    for div in ("fbs", "fcs"):
        old = json.loads((output / "v05" / f"{div}.json").read_text())["teams"]
        new = json.loads((output / "v06" / f"{div}.json").read_text())["teams"]
        old_by_id = {t["id"]: t for t in old}
        new_by_id = {t["id"]: t for t in new}
        if old_by_id.keys() != new_by_id.keys():
            raise ValueError("Model team universes differ")
        changes = [{"team": t["name"], "conference": t["conference"], "previous_rank": t["rank"],
                    "new_rank": new_by_id[t["id"]]["rank"],
                    "movement": t["rank"] - new_by_id[t["id"]]["rank"]}
                   for t in old]
        changed_top25 = [t["name"] for t in new[:25] if old_by_id[t["id"]]["rank"] > 25]
        conference = defaultdict(list)
        for t in changes:
            conference[t["conference"]].append(t["movement"])
        report["divisions"][div] = {
            "team_count": len(changes),
            "average_absolute_movement": round(sum(abs(t["movement"]) for t in changes) / len(changes), 3),
            "top25_new_entries": changed_top25,
            "top10_new_entries": [t["name"] for t in new[:10] if old_by_id[t["id"]]["rank"] > 10],
            "largest_risers": sorted(changes, key=lambda t: -t["movement"])[:10],
            "largest_fallers": sorted(changes, key=lambda t: t["movement"])[:10],
            "conference_mean_movement": {k: round(sum(v)/len(v), 3) for k, v in sorted(conference.items())},
            "all_changes": changes
        }
    (output / "movement-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: {j: v for j, v in d.items() if j != "all_changes"}
                      for k, d in report["divisions"].items()}, indent=2))
    return report

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--season", required=True, type=int)
    p.add_argument("--as-of", required=True)
    a = p.parse_args()
    compare(a.source, a.output, a.season, a.as_of)
