# Requirements: <App or feature>

| Version | Status | Owner | Approvers |
|---|---|---|---|
| 0.1 | Draft | <product owner> | <product owner, tech lead> |

## 1. Brief
- **Problem:** <who has which problem today>
- **Goals and KPIs:** <measurable, e.g. "D30 retention ≥ 25%">
- **Target users:** <personas, the devices they use, accessibility needs>
- **In scope:** <…>
- **Out of scope:** <…>
- **Constraints:** <deadline, budget, team, mandated backend or SDKs, compliance>
- **Top risks:** <see the STATUS risk register>

## 2. Functional requirements
| ID | User story | Priority (M/S/C/W) | Acceptance criteria (Given / When / Then) |
|---|---|---|---|
| FR-001 | As a <user>, I want <goal>, so that <value> | M | Given … when … then …<br>Offline: …<br>Error: … |

## 3. Non-functional requirements
| ID | Requirement | Target and condition | Verified by |
|---|---|---|---|
| NFR-PERF-01 | Cold start | p90 ≤ <n> s on <reference device> | Macrobenchmark |
| NFR-REL-01 | Stability | Crash rate < <n>% and ANR rate < <n>%, both below Play's thresholds | Android vitals |
| NFR-REL-02 | Offline | <what works offline> | System test |
| NFR-SIZE-01 | Download size | ≤ <n> MB | Play Console |
| NFR-A11Y-01 | Accessibility | Usable with TalkBack; 200% font; 48 dp targets; 4.5:1 contrast | Accessibility test pass |
| NFR-I18N-01 | Languages | <locales>; RTL <yes/no> | Pseudo-locale tests |
| NFR-SEC-01 | Security level | MASVS-<L1/L2> | MASVS checklist |
| NFR-PRIV-01 | Privacy | <consent, retention, account deletion> | Privacy review |
| NFR-MAINT-01 | Maintainability | Lint and detekt clean; coverage ≥ <n>% in domain and ViewModels | CI |

## 4. Platform and devices
| Item | Value |
|---|---|
| minSdk / targetSdk | <n> (audience data: <source>) / Play's required level |
| Form factors | Phone · Tablet · Foldable · Wear, TV or Auto (in or out of scope) |
| Orientations | Portrait · Landscape |
| Reference low-end device | <model, RAM> |
| Distribution | <countries>; Google Play only, or other stores too |

## 5. Permissions inventory
| Permission | Why (FR) | When requested | If denied | Alternatives considered |
|---|---|---|---|---|
| e.g. `POST_NOTIFICATIONS` | FR-010 reminders | When the first reminder is set | Reminders off; a banner in settings | — |

## 6. Data inventory
This section feeds the Play Data safety form.

| Data type | Purpose | Stored (device / server) | Encrypted | Shared with (including SDKs) | Retention |
|---|---|---|---|---|---|

## 7. External interfaces
| Interface | Owner | Contract (link, status) | Environments | Notes |
|---|---|---|---|---|
| Backend REST API | | OpenAPI <link> | dev / staging / prod | |
| Third-party SDKs | | | | |
| Deep links / push | | | | |

## 8. Acceptance outline
One `AT-` scenario per Must FR, kept in [test-plan.md](test-plan.md) §5.

## 9. Assumptions and open items
- ASSUMPTION: <…>
- TBD-1: <…>

## 10. Sign-off
| Role | Name | Decision | Date |
|---|---|---|---|
