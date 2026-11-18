# Requirements traceability matrix: <App or feature>

Every requirement traces forward to design, code, tests and the release. Every test traces back to a requirement. Update this file in the same PR as the change.

Upstream source cites the backend or other inputs with a prefix (e.g. `BE-FR-002`); use "—" when the requirement is the app's own.

| Req ID | Summary | Priority | Upstream source | Design (architecture § / feature design) | Code (module, PRs) | Tests (IDs) | Result | Release |
|---|---|---|---|---|---|---|---|---|
| FR-001 | View the notes list | M | BE-FR-002 | design/notes.md §1 | feature:notes, #12 #14 | UT-003, IT-001, UI-001, AT-001 | Pass | 1.0.0 |
| NFR-PERF-01 | Cold start ≤ <n> s | M | — | architecture.md §1 | app (Baseline Profile) | ST-010 | | |

## Coverage checks
| Check | Required |
|---|---|
| Requirements without a design | 0 at G3 |
| Must requirements without a passing test | 0 at G5 |
| Tests without a requirement | 0 (trace them, or remove them) |
