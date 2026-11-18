# STATUS: <Initiative name>

> The control file for the Android SDLC workflow. Claude reads it first to resume work.
>
> Keep it current. It's the single place for gate decisions, risks and open items.

| Field | Value |
|---|---|
| Initiative | <name> (`docs/sdlc/<initiative-slug>/`) |
| Type | New app / Feature in <app> |
| Application ID | e.g. `com.example.notes` |
| SDK levels | minSdk <n> · targetSdk <n> · compileSdk <n> |
| Module layout | Layer modules / Feature + core modules (ADR-<n>) |
| Security level | MASVS-L1 / L2 (+R) |
| Compliance | e.g. GDPR, COPPA, Google Play policies |
| Product owner / Tech lead | <name, role> / <name, role> |
| Inputs | e.g. backend contract `<repo>/docs/api/openapi.yaml` v<x>, design `<link>` (or "none") |
| Code review mode | Approve before writing / Review after writing (each PR) |
| Current phase | 1 Requirements |
| Tailoring | Full (app) / Light (feature) |
| Last updated | YYYY-MM-DD |

## Deliverables
| Phase | Deliverable | File | Status (Not started / Draft / In review / Approved) | Version |
|---|---|---|---|---|
| 1 | Requirements | requirements.md | Not started | — |
| 1–6 | RTM | rtm.md | Not started | — |
| 2 | Architecture + threat model | architecture.md | Not started | — |
| 2+ | ADRs | adr/NNNN-<decision>.md | — | — |
| 1–5 | Test plan + summary report | test-plan.md | Not started | — |
| 3 | Feature designs | design/<feature>.md | Not started | — |
| 6 | Release checklist | release-checklist.md | Not started | — |

## Gate log
Decision is one of: Approved / Approved with conditions / Rejected / Waived.

| Gate | Date | Decision | Approver (name, role) | Conditions or accepted risk | Tag |
|---|---|---|---|---|---|
| G1 Requirements baseline | | | | | |
| G2 Architecture baseline | | | | | |
| G3 Ready to build | | | | | |
| G4 Code complete | | | | | |
| G5 Release readiness | | | | | |
| G6 Launch accepted | | | | | |

## Decisions
| Date | Decision | Recorded in (ADR / minutes) |
|---|---|---|

## Risks
| ID | Risk ("If …, then …") | Likelihood (H/M/L) | Impact (H/M/L) | Owner | Mitigation | Status |
|---|---|---|---|---|---|---|
| R-01 | | | | | | Open |

## Change requests
| CR ID | Title | Status | Affected items | Decision date |
|---|---|---|---|---|

## Open items
A TBD that blocks a Must requirement blocks the gate.

| ID | Type (TBD / ASSUMPTION / Question) | Description | Blocks gate? | Owner | Status |
|---|---|---|---|---|---|
