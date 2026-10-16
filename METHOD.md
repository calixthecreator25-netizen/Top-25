# College Football Merit Poll methodology

## In season
After the first four completed regular-season weeks: results-only rankings, without committee overrides or preseason carryover. Opponent quality, strength of schedule, wins/losses and empirically earned conference strength determine rank. FBS and FCS have separate official lists; interdivision games affect opponent quality.

### Experimental implementation (v0.5; not official)
The experimental in-season score uses **50% schedule strength, 25% result quality, 15% win percentage, and 10% conference strength**. The prior **v0.4** formula (40/30/20/10) remains the historical reference. The candidate was selected using 2023–2024 development games and evaluated once on 2025 holdout games: 783/1,148 (68.21%) versus v0.4's 773/1,148 (67.33%). This small predictive advantage does not establish ranking fairness or guaranteed future superiority. Opponent ratings are calculated iteratively from completed Division I head-to-head results; they are *not* recruiting or brand prestige ratings.

- **Schedule strength:** mean opponent rating for completed games against Division I teams.
- **Result quality:** opponent rating for a win, half the opponent rating for a tie, and zero for a loss, averaged across Division I games. Losing to a strong opponent may improve the schedule component, but is not treated as a quality win.
- **Win percentage:** completed games including games against lower divisions. Lower-division opponents do not receive invented ratings; those games are excluded from schedule and result-quality components.
- **Conference strength:** smoothed average of results and opponent ratings in interconference Division I games; a neutral value is used when no such games are available. Each team record now exposes the number of interconference result observations supporting its conference rating. These are team-game observations, not necessarily distinct games.
- **No-game teams:** sorted below teams with completed games, with their neutral components clearly marked as placeholders. A score gap across that boundary is not meaningful.
- **Limitations:** the opponent model and conference calibration have not been independently validated. Missing opponent ratings can create uneven coverage. This is a demonstration, not a claim of objective certainty or an official Top 25.

## Preseason
The preseason FBS Top 12 is reserved for the previous season's 12 playoff teams, ordered by advancement: champion, runner-up, semifinal losers, quarterfinal losers, and first-round losers. Prior-year merit breaks ties within advancement tiers. Preseason places #13–25 go to the highest-scoring remaining teams by verified roster talent.

**Publication schedule:** Publish the preseason Top 25, then publish no new official rankings during Weeks 1–4 of the regular season. After Week 4 is completed, publish the first regular-season Top 25 using only completed-game merit under the 50/25/15/10 formula. Continue publishing merit-based rankings each Monday thereafter. The first four weeks have no blended or transitional poll, and preseason positions provide no carryover once regular-season rankings begin. The Week-4 cutoff is universal across FBS programs, regardless of when conference play starts.

**Implementation status:** The preseason generator produces the playoff-seeded opening poll, and the experimental in-season generator computes pure-merit rankings. The publication hold through Week 4 and automatic first post-Week-4 release are policy specifications not yet enforced by the publishing workflow; early-season experimental rankings must not be described as official weekly polls.

Roster talent weights: returning talent 35%, transfers 20%, recruiting 15%, QB/key positions 15%, coaching continuity 10%, depth 5%. All factors are normalized to 0–100. No rating may be published without verified input provenance. FCS has its own all-team preseason talent table.

## Transparency
Every team profile must show score components, data source, last refresh, games, opponents, and why the team ranks below the one above it. Missing data must be labeled, never treated as zero.

## Status
The repository publishes an **experimental**, automatically generated FBS/FCS rankings database on GitHub Pages. The official poll is not launched. Weekly ChatGPT reporting is separate from GitHub deployment.