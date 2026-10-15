# Preseason data intake

The preseason engine reads a JSON object with `season`, `fbs_teams`, `fcs_teams`, and `playoff_finish`. Each team requires a stable `id`, `name`, `source_url`, `source_checked_at`, and six normalized 0–100 talent factors: `returning_talent`, `transfers`, `recruiting`, `key_positions`, `coaching_continuity`, `depth`.

Playoff finish requires exactly 12 distinct FBS teams: champion (1), runner-up (1), semifinal (2), quarterfinal (4), first-round (4), plus previous-year merit for same-round ordering.

This schema checks the data supplied, but does not certify the completeness of NCAA membership or validity of upstream scouting grades. Do not publish until source reconciliation and coverage checks pass.

Run `python scripts/preseason.py input.json output.json` once verified inputs are available.
