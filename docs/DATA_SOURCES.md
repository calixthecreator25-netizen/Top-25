# Data feeds and publication gates

## Current status
The repository contains a source-ingestion script and scheduled GitHub workflow, but it does not have a verified live feed until a valid CollegeFootballData API key is added as the repository secret `CFBD_API_KEY` and the workflow successfully runs.

## Scope
The script requests FBS team lists, all teams, FBS games and FCS games. All-teams responses must be reconciled to an authoritative season-specific FBS/FCS membership roster. CollegeFootballData's all-teams endpoint may include programs outside the target scope; do not infer FCS membership simply by subtracting FBS.

## Preseason roster talent
The source snapshots alone do not provide the six normalized talent ratings. Build an audited adapter for returning production, transfers, recruiting, key positions, coaching and depth, with licensing and source coverage reviewed before official publication.

## Publication gates
1. Verify season-specific FBS and FCS membership and transition status.
2. Verify all scheduled/completed game coverage, dates and opponent IDs.
3. Reconcile conference memberships and calculate empirically earned conference strength.
4. Audit rating formula, early-season behavior, interdivision effects and score provenance.
5. Publish only after all checks pass; otherwise show unavailable status.

## Schedule
The weekly GitHub snapshot workflow runs at 11:00 UTC Mondays, which is **not** consistently 7:00 a.m. Central due to daylight saving time. It is data collection only, not the official publication clock. The existing ChatGPT Monday 7:00 a.m. Central reminder is separate.
