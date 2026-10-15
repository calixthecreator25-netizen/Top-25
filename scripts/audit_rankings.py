"""Audit experimental rankings for data integrity and noteworthy comparisons."""
import argparse
import json
from pathlib import Path

def audit(folder):
    folder = Path(folder)
    output = []
    for division in ("fbs", "fcs"):
        payload = json.loads((folder / (division + ".json")).read_text())
        teams = payload["teams"]
        assert teams, f"{division}: no teams"
        assert len({t["id"] for t in teams}) == len(teams), f"{division}: duplicate teams"
        assert [t["rank"] for t in teams] == list(range(1, len(teams)+1)), f"{division}: nonconsecutive ranks"
        output.append(f"## {division.upper()} — {len(teams)} teams")
        output.append("| Rank | Team | Record | Merit | SOS | Results | Win % | Conference |")
        output.append("|---:|---|---:|---:|---:|---:|---:|---:|")
        for t in teams[:25]:
            c=t["components"]
            output.append(f'| {t["rank"]} | {t["name"]} | {t["wins"]}-{t["losses"]} | {t["merit_score"]:.2f} | {c["schedule_strength"]:.2f} | {c["result_quality"]:.2f} | {c["win_percentage"]:.2f} | {c["conference_strength"]:.2f} |')
        output.append("")
        undefeated = [t for t in teams if t["losses"] == 0 and t["wins"] >= 3]
        one_loss = [t for t in teams if t["losses"] == 1]
        inversions = [(a,b) for a in one_loss for b in undefeated if a["rank"] < b["rank"]]
        output.append(f"### Review queue: {len(inversions)} one-loss-over-undefeated comparisons")
        for a,b in inversions[:30]:
            output.append(f'- #{a["rank"]} {a["name"]} ({a["wins"]}-{a["losses"]}) over #{b["rank"]} {b["name"]} ({b["wins"]}-{b["losses"]}); merit difference {a["merit_score"]-b["merit_score"]:.2f}')
        output.append("")
        missing = sum(t.get("lower_division_games",0) for t in teams)
        output.append(f"Lower-division games counted in records: {missing}. Their opponents are not rated for SOS or result quality.")
        output.append("")
    return "\n".join(output)+"\n"

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",default="data/experimental")
    p.add_argument("--output",default="site/audit.md")
    args=p.parse_args()
    report=audit(args.source)
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text("# Experimental rankings audit\n\n"+report)
    print(report[:1500])
