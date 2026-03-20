---
name: standup
description: "Use when: daily standup, status update, progress report, what did I do yesterday, daily summary, end of day recap, morning standup, weekly summary, sprint review. Aggregates git log and GSD task state into a formatted daily summary."
version: 1.0.0
---

# `/standup` — Daily Summary Generator

> Aggregates git commits from the last 24 hours and GSD task state into a structured daily standup report — so your team (or your future self) knows exactly what happened and what is next.

---

## When to Use This Skill

Invoke `/standup` when you need:

| Trigger | Example | Subcommand |
|---------|---------|------------|
| Daily standup | Morning sync with team, async standup update | (none — default 24h) |
| End-of-day summary | Recap before closing the laptop | (none — default 24h) |
| Progress check | "What did I actually ship this week?" | `week` |
| Custom timeframe | Review last 48h of activity | `48h` |
| Team update | Async standup for distributed teams | (none — default 24h) |

**Key signals in user messages**: "standup", "daily summary", "what did I do", "yesterday", "progress update", "end of day", "weekly recap", "what have I been working on"

---

## Usage

```
/standup               Default: last 24 hours of activity
/standup 48h           Custom timeframe: last 48 hours
/standup 72h           Custom timeframe: last 72 hours
/standup week          Last 7 days (equivalent to 168h)
```

---

## Behavior

This skill collects raw data via a helper script, then Claude formats it into a structured standup report.

### Step 1: Run the Data Collection Script

Execute `scripts/standup.sh` from the skill directory (or the repo root if standup.sh is on PATH):

```bash
# Default 24 hours
bash skills/standup/scripts/standup.sh

# Custom timeframe
bash skills/standup/scripts/standup.sh 48h
bash skills/standup/scripts/standup.sh week
```

The script outputs structured sections to stdout: git activity, task state, and next-up information.

### Step 2: Format the Output

Claude reads the script output and formats it into a standup report:

```
## Daily Standup — YYYY-MM-DD

### Completed
- [commit summaries, grouped by topic where possible]
- [each bullet = one logical unit of work]

### In Progress
- [from STATE.md current position: Phase X, Plan Y]
- [status description if available]

### Blockers
- [from STATE.md blockers section, or "None"]

### Next
- [from ROADMAP.md: next incomplete phase or plan]
```

### Step 3: Interpret and Present

- Group related commits under a single bullet (e.g., 3 commits for the same feature → one bullet)
- Extract the essence of each work item — avoid commit message verbatim copy if it's cryptic
- Flag if no commits were found in the timeframe (may indicate work on another branch or repo)
- Note if STATE.md was not found (project may not use GSD)

---

## Gotchas

### Timezone Sensitivity

`git log --since` uses the local system timezone. If you commit across timezones (e.g., working on a laptop that traveled across zones, or in a CI environment with UTC), some commits may be missed or double-counted near the boundary. Always verify the time range displayed in the script output matches your expected window. If the commit count looks wrong, pass an explicit hour count (e.g., `48h`) rather than relying on boundary alignment.

### Shallow Clone Limitation

In CI environments or freshly-checked-out repos created with `--depth`, git log may not contain full history beyond the shallow boundary. Commits that occurred before the shallow cutoff will not appear in the output, even if they fall within the requested time window. The script detects shallow repos (`git rev-parse --is-shallow-repository`) and prints a warning. If you see the warning, run `git fetch --unshallow` to restore full history before using `/standup`.

### Multi-Repo Projects

`standup.sh` runs in the current repository only. For projects that span multiple repos (e.g., a monorepo split, separate frontend/backend repos, or a mobile app with a separate API repo), each repo requires a separate run. To consolidate activity across repos, run `/standup` in each repo and manually combine the Completed sections. Alternatively, specify an absolute path as a future enhancement — see the `--repo` flag in the script's `--help` output.

---

## Setup

On first invocation, this skill checks for a config file at `${CLAUDE_PLUGIN_DATA}/standup/config.json`. If it does not exist, ask the user for initial configuration using AskUserQuestion:

```json
{
  "author_name": null,
  "repos": ["."],
  "output_format": "markdown",
  "include_gsd_state": true,
  "slack_channel": null,
  "default_timeframe": "24h"
}
```

- `author_name`: Filter git log to this author (null = all authors in the repo)
- `repos`: List of repository paths to aggregate (default: current directory only)
- `output_format`: "markdown" (default), "slack" (compact for Slack), or "json"
- `include_gsd_state`: Whether to read STATE.md and ROADMAP.md for In Progress / Next sections
- `slack_channel`: If set, remind Claude to format for Slack posting
- `default_timeframe`: Default hours for the standup window

If config exists, load it before running standup.sh and apply as defaults.

---

## Evaluations

Test these scenarios to verify the skill works correctly:

| Scenario | Input | Expected Behavior |
|----------|-------|-------------------|
| Basic daily standup | `/standup` | Runs standup.sh, groups commits by topic, shows In Progress from STATE.md |
| Empty commit history | `/standup` (no commits in 24h) | Reports "No commits in the last 24h" cleanly, still shows In Progress/Next |
| Custom timeframe | `/standup week` | Shows 7 days of activity, correctly handles date boundaries |
| Non-GSD project | `/standup` (no .planning/) | Shows git activity only, omits In Progress/Next gracefully |
| Multi-repo | Config with `repos: [".", "../api"]` | Aggregates commits from both repos in one report |

---

## Related Skills

| Skill | Path | When to Chain |
|-------|------|---------------|
| tps-kaizen | `skills/tps-kaizen/SKILL.md` | If the standup reveals a pattern of repeated blockers or recurring failures — use `/tps-kaizen five-whys` to investigate the structural cause |
| qc-audit | `skills/qc-audit/SKILL.md` | After a weekly standup — use `/qc-audit trend` to check whether quality metrics align with the shipping velocity shown in the standup |
