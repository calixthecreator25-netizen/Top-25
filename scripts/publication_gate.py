"""Publication gate: no weekly Top 25 releases during the first 28 days of football."""
import argparse
import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo

CENTRAL = ZoneInfo("America/Chicago")

def first_regular_game(source, season):
    dates = []
    for division in ("fbs", "fcs"):
        file = Path(source) / f"{division}_games_{season}.json"
        games = json.loads(file.read_text(encoding="utf-8"))["records"]
        for game in games:
            if str(game.get("seasonType", "regular")).lower() not in ("regular", "regular_season"):
                continue
            if game.get("startDate"):
                day = dt.date.fromisoformat(game["startDate"][:10])
                if day.year == season:
                    dates.append(day)
    if not dates:
        raise ValueError("No dated regular-season games; refusing to publish")
    return min(dates)

def first_merit_date(start):
    """First Monday at least 28 days after the opening regular-season game."""
    threshold = start + dt.timedelta(days=28)
    return threshold + dt.timedelta(days=(7-threshold.weekday()) % 7)

def may_publish(source, season, today=None):
    if today is None:
        today = dt.datetime.now(CENTRAL).date()
    start = first_regular_game(source, season)
    release = first_merit_date(start)
    # Never automatically republish past or future seasons.
    return today.year == season and today >= release, start, release

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source", default="data/raw")
    p.add_argument("--season", type=int, required=True)
    p.add_argument("--github-output")
    a = p.parse_args()
    allowed, start, release = may_publish(a.source, a.season)
    print(f"Season starts: {start}; first merit publication: {release}; publish: {allowed}")
    if a.github_output:
        with open(a.github_output, "a", encoding="utf-8") as f:
            f.write(f"publish={'true' if allowed else 'false'}\n")
            f.write(f"first_merit_date={release}\n")
