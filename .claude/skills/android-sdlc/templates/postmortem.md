# PM-NNN: <Incident title>

| Severity | Date of incident | Author | Reviewed by | Status |
|---|---|---|---|---|
| S1 | YYYY-MM-DD | <name> | <tech lead, product owner> | Draft / Reviewed / Actions done |

> Blameless: describe what the system and the process allowed, not who made a mistake.

## Summary
<Two or three sentences: what broke, for whom, for how long, and how it was fixed.>

## Impact
| Item | Value |
|---|---|
| Users affected | <number or share of users; versions; device models> |
| Duration | <from first user impact to the fix reaching most users> |
| Effect | <e.g. crash on launch, orders lost, data exposed> |
| Requirements broken | <FR / NFR IDs> |

## Timeline (UTC)
| Time | Event |
|---|---|
| | First user impact |
| | Detected (by which alert, report or person) |
| | Contained (rollout halted, kill switch off) |
| | Fix released |
| | Resolved |

## Root cause
Ask "why?" until you reach a cause the team can change.
1. Why did users see the problem?
2. Why did the code behave that way?
3. Why didn't a test, review or the staged rollout catch it?

## What went well, what went badly
- **Went well:** <…>
- **Went badly:** <…>
- **Lucky:** <what limited the damage by chance>

## Action items
Each prevents, detects earlier, or reduces the impact of the next incident like this one.

| ID | Action | Type (prevent / detect / mitigate) | Owner | Due | Tracked in (CR / ticket) | Status |
|---|---|---|---|---|---|---|
| PM-NNN-1 | e.g. Add a test that reproduces the crash | Prevent | | | | Open |

## Traceability
- **New or changed tests:** <test IDs; the RTM rows updated>
- **Documents to update:** <architecture, ADRs, feature designs, runbook>
