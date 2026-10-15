# College Football Merit Poll methodology

## In season
Results-only rankings, without committee overrides or preseason carryover. Opponent quality, strength of schedule, wins/losses and empirically earned conference strength determine rank. FBS and FCS have separate official lists; interdivision games affect opponent quality.

### Experimental implementation (v0.4; not official)
The experimental in-season score uses **40% schedule strength, 30% result quality, 20% win percentage, and 10% conference strength**. Opponent ratings are calculated iteratively from completed Division I head-to-head results; they are *not* recruiting or brand prestige ratings.

- **Schedule strength:** mean opponent rating for completed games against Division I teams.
- **Result quality:** opponent rating for a win, half the opponent rating for a tie, and zero for a loss, averaged across Division I games. Losing to a strong opponent may improve the schedule component, but is not treated as a quality win.
- **Win percentage:** completed games including games against lower divisions. Lower-division opponents do not receive invented ratings; those games are excluded from schedule and result-quality components.
- **Conference strength:** smoothed average of results and opponent ratings in interconference Division I games; a neutral value is used when no such games are available. Each team record now exposes the number of interconference result observations supporting its conference rating. These are team-game observations, not necessarily distinct games.
- **No-game teams:** sorted below teams with completed games, with their neutral components clearly marked as placeholders. A score gap across that boundary is not meaningful.
- **Limitations:** the opponent model and conference calibration have not been independently validated. Missing opponent ratings can create uneven coverage. This is a demonstration, not a claim of objective certainty or an official Top 25.

## Preseason
Previous year's 12 playoff teams take FBS places 1–12, ordered by advancement: champion; runner-up; semifinal losers; quarterfinal losers; first-round losers. Prior-year merit breaks ties within each tier. The other 13 places are awarded by current roster talent.

Roster talent weights: returning talent 35%, transfers 20%, recruiting 15%, QB/key positions 15%, coaching continuity 10%, depth 5%. All factors are normalized to 0–100. No rating may be published without verified input provenance. FCS has its own all-team preseason talent table.

## Transparency
Every team profile must show score components, data source, last refresh, games, opponents, and why the team ranks below the one above it. Missing data must be labeled, never treated as zero.

## Status
The repository publishes an **experimental**, automatically generated FBS/FCS rankings database on GitHub Pages. The official poll is not launched. Weekly ChatGPT reporting is separate from GitHub deployment.