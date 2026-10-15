"""Persist dated experimental snapshots and annotate movement from the prior date."""
import argparse, json, shutil
from pathlib import Path

def archive(current, history):
    current, history = Path(current), Path(history)
    history.mkdir(parents=True, exist_ok=True)
    manifest = history / "index.json"
    dates = set(json.loads(manifest.read_text())["dates"]) if manifest.exists() else set()
    for division in ("fbs", "fcs"):
        source = current / (division + ".json")
        payload = json.loads(source.read_text())
        date = payload["as_of"]
        target = history / date / (division + ".json")
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copyfile(source, target)
        previous = sorted((d for d in dates if d < date), reverse=True)
        prior_file = next((history / d / (division + ".json") for d in previous
                           if (history / d / (division + ".json")).exists()), None)
        prior = {str(t["id"]):t for t in json.loads(prior_file.read_text())["teams"]} if prior_file else {}
        for t in payload["teams"]:
            old = prior.get(str(t["id"]))
            t["previous_rank"] = old["rank"] if old else None
            t["rank_change"] = old["rank"] - t["rank"] if old else None
            t["previous_merit_score"] = old["merit_score"] if old else None
        source.write_text(json.dumps(payload,separators=(",",":")))
        dates.add(date)
    manifest.write_text(json.dumps({"dates":sorted(dates,reverse=True)},indent=2)+"\n")
    print("Archived experimental dates:",", ".join(sorted(dates,reverse=True)))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--current",default="data/experimental")
    p.add_argument("--history",default="data/history")
    a=p.parse_args()
    archive(a.current,a.history)
