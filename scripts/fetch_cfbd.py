#!/usr/bin/env python3
"""Fetch CFBD source snapshots without publishing unverified rankings.

Set CFBD_API_KEY in environment. Fetches team lists and calendar-year games
from the CollegeFootballData API. API responses are source material, not
automatically certified NCAA membership or official merit rankings.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode

BASE = "https://api.collegefootballdata.com"
ENDPOINTS = {
    "fbs_teams": "/teams/fbs",
    "all_teams": "/teams",
    "fbs_games": "/games",
}

def get_json(path, params, token):
    url = BASE + path + ("?" + urlencode(params) if params else "")
    req = Request(url, headers={"Authorization": "Bearer " + token, "Accept": "application/json", "User-Agent": "college-football-merit-poll/0.1"})
    with urlopen(req, timeout=45) as response:
        return json.load(response)

def fetch(season, output_dir, token):
    if not token:
        raise ValueError("CFBD_API_KEY is required; no live data fetched")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for name, endpoint, params in [
        ("fbs_teams", ENDPOINTS["fbs_teams"], {"year": season}),
        ("all_teams", ENDPOINTS["all_teams"], {"year": season}),
        ("season_records", "/records", {"year": season}),
        ("fbs_games", ENDPOINTS["fbs_games"], {"year": season, "division": "fbs"}),
        ("fcs_games", ENDPOINTS["fbs_games"], {"year": season, "division": "fcs"}),
    ]:
        data = get_json(endpoint, params, token)
        if not isinstance(data, list):
            raise ValueError(f"Unexpected response for {name}")
        payload = {"source": "CollegeFootballData", "endpoint": endpoint,
                   "parameters": params, "fetched_at": timestamp,
                   "season": season, "record_count": len(data), "records": data}
        (output_dir / f"{name}_{season}.json").write_text(json.dumps(payload, indent=2)+"\n", encoding="utf-8")
        print(f"{name}: {len(data)} source records")
    print("Source snapshots collected. Rankings NOT generated or published.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/raw"))
    args = parser.parse_args()
    fetch(args.season, args.output, os.getenv("CFBD_API_KEY"))
