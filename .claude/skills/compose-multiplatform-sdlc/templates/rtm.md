# Requirements traceability matrix: <App or feature>

Every requirement traces forward to design, code, tests and the release on each of its platforms. Every test traces back to a requirement. Update this file in the same PR as the change.

| Req ID | Summary | Priority | Platforms | Design (architecture § / feature design) | Code (module / source set, PRs) | Tests (IDs) | Result (Android / iOS) | Release (Android / iOS) |
|---|---|---|---|---|---|---|---|---|
| FR-001 | View the notes list | M | Both | design/notes.md §1 | feature:notes `commonMain`, #12 #14 | UT-003, IT-001, UI-001, AT-001 | Pass / Pass | 1.0.0 / 1.0.0 |
| FR-010 | Share a note | S | Both | design/notes.md §4 | feature:notes `commonMain`, core:platform `androidMain` + `iosMain`, #20 | IT-002, IT-003, AT-004 | | |
| NFR-PERF-01 | Cold start ≤ <n> s | M | Both | architecture.md §1 | androidApp (Baseline Profile), shared | ST-010, ST-011 | | |

## Coverage checks
| Check | Required |
|---|---|
| Requirements without a design | 0 at G3 |
| Must requirements without a passing test on each of their platforms | 0 at G5 |
| Platform matrix rows without a test on their platform | 0 at G5 |
| Tests without a requirement | 0 (trace them, or remove them) |
