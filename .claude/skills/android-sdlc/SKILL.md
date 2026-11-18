---
name: android-sdlc
description: Waterfall lifecycle for building a native Android app or feature in Kotlin - requirements, architecture, detailed design, implementation, testing, Google Play release and maintenance - with phase gates, sign-offs, traceability and change control. Bundles Android best practices (Clean Architecture + MVVM, Jetpack Compose + Material 3, Hilt, Coroutines/Flow, Room, OWASP MASVS security, testing, performance, accessibility), canonical Kotlin code patterns, a PR review checklist and deliverable templates (requirements, architecture, ADR, feature design, test plan, release checklist). Use when planning, designing, building, testing or releasing an Android/Kotlin app or feature phase by phase, when writing any of those documents for an Android project, or when the user mentions waterfall, SDLC, V-model or phase gates for Android.
---

# Android SDLC (waterfall)

A gated, document-driven lifecycle for building a native Android app in Kotlin, or a feature in an existing one. Each phase produces reviewed deliverables and ends at a gate. The next phase starts only after an explicit sign-off.

## Principles
- **Quality is designed in.** Each design phase writes the tests that later verify it (see the [V-model](#v-model)). Every NFR has a measurable target.
- **Traceable.** Every requirement has an ID that is carried into design, code, tests and the release ([RTM](templates/rtm.md)).
- **Gates are real.** A baselined deliverable changes only through a [change request](templates/change-request.md).
- **Opinionated defaults, explicit deviations.** The [default stack](reference/architecture.md#default-stack) applies unless an ADR says otherwise.
- **Project rules win.** If the target repo has a `CLAUDE.md` or `.claude/rules/`, they override this skill's conventions. This skill still governs the process and the quality bars.
- **Proportionate depth.** Write as much as the risk needs. A feature gets lighter documents than a new app; see [Tailoring](#tailoring-app-vs-feature).
- **Reviewable output.** Documents follow fixed templates. Code follows one [pattern per concern](reference/code-patterns.md). PRs are small and single-purpose ([review checklist](reference/review-checklist.md)).

## Lifecycle
| # | Phase | Key question | Main deliverables | Gate |
|---|---|---|---|---|
| 1 | [Requirements](phases/1-requirements.md) | What must the app do, and how well? | Requirements (brief, FRs, NFRs, permissions, data inventory), acceptance outline, RTM | G1 Requirements baseline |
| 2 | [Architecture](phases/2-architecture.md) | How is the app structured, and on which stack? | Architecture document, ADRs, threat model, master test plan | G2 Architecture baseline |
| 3 | [Detailed design](phases/3-detailed-design.md) | How is each feature built? | Feature designs (screens, state, contracts, schema, PR plan), integration test cases | G3 Ready to build |
| 4 | [Implementation](phases/4-implementation.md) | Is it built right? | Code and unit tests, CI quality gates, release candidate | G4 Code complete |
| 5 | [Testing](phases/5-testing.md) | Does it meet the spec on real devices? | Test reports, UAT sign-off, test summary report | G5 Release readiness (go/no-go) |
| 6 | [Release](phases/6-release.md) | Is it live on Google Play, and stable? | Release checklist, rollout record, handover | G6 Launch accepted |
| 7 | [Maintenance](phases/7-maintenance.md) | Does it stay healthy as Android and Play change? | Vitals reviews, CRs, hotfixes, yearly target-SDK update | Mini-cycle per change |

## V-model
| Design phase | Verified in Phase 5 by | Test basis written in |
|---|---|---|
| 1 Requirements | Acceptance tests (UAT on the Play internal or closed track) | Phase 1: acceptance outline |
| 2 Architecture | System and NFR tests on the device matrix: startup, jank, security, accessibility, offline, upgrade | Phase 2: master test plan |
| 3 Detailed design | Integration tests (Room, API, navigation) and Compose UI tests | Phase 3: feature designs |
| 4 Implementation | Unit tests (domain, data, ViewModels) | Phase 4: written with the code |

## Tailoring: app vs feature
| Deliverable | New app | Feature in an existing app |
|---|---|---|
| [Requirements](templates/requirements.md) | Full | Brief, feature FRs, changed NFRs, new permissions and data |
| [Architecture](templates/architecture.md) | Full, with stack and module ADRs | Delta: changed modules, data flows and threats |
| [ADRs](templates/adr.md) | Stack deviations, module layout, other key choices | One per significant decision |
| [Feature design](templates/feature-design.md) | One per feature | One for the feature |
| [Test plan](templates/test-plan.md) | Master plan and summary report | Feature scope plus regression scope |
| [Release checklist](templates/release-checklist.md) | Full, with hypercare | Standard; rollout behind a feature flag |
| [STATUS](templates/status.md), [RTM](templates/rtm.md) | Required | Required (feature rows only) |

A small feature may combine G2 and G3 into one review. **G5 is never skipped or combined.**

## How Claude runs this workflow
1. **Workspace.** In the target project, open `docs/sdlc/<initiative-slug>/STATUS.md`. If it exists, resume at the phase it records. If not, create it from [templates/status.md](templates/status.md).
2. **Facts.**
   - In an existing Android project, read `settings.gradle.kts`, `gradle/libs.versions.toml`, the module `build.gradle.kts` files, `CLAUDE.md` and `.claude/rules/`. Record the modules, `minSdk`/`targetSdk`/`compileSdk` and the stack in STATUS.md. Don't contradict them without an ADR.
   - When a backend, an API contract or a design already exists, read them as inputs:
     - the contract (e.g. OpenAPI);
     - the backend's own requirements, and the rules it sets for clients (headers, retries, polling, minimum app versions);
     - every screen of the design.

     Record each source in STATUS.md. Cite upstream IDs with a prefix (e.g. `BE-FR-003`), so they don't clash with the app's own, and fill the RTM's **Upstream source** column.
3. **Scope.** Confirm with the user:
   - new app or feature;
   - target users and devices;
   - compliance (e.g. GDPR, COPPA, HIPAA) and the MASVS level;
   - existing documents to reuse;
   - how the owner reviews code in Phase 4: approve each PR's code before it's written, or review each PR after it's written.

   Record the answers and pick the tailoring column.
4. **Load only what's needed:** the current phase file and the references its **Load** line lists. If STATUS.md doesn't show the previous gate as approved, stop and say so.
5. **Write the deliverables** from `templates/` into the workspace.
   - Mark unknowns `TBD-<n>` and assumptions `ASSUMPTION:`, and list them in STATUS.md.
   - Ask the user for what only stakeholders can decide: targets, priorities, approvers.
   - Never invent requirements, numbers, approvals or sign-offs.
   - Mark any number Claude suggests (an NFR target, a limit) as **(proposed)**. Confirming those numbers is a TBD that blocks G1.
6. **Trace.** Add every new requirement, design element and test to `rtm.md`.
7. **Gate review.** Run the phase's exit checklist. Present the deliverables and their status, the checklist results, open TBDs, top risks, and a recommendation: approve, approve with conditions, or rework.
8. **STOP for sign-off.** Ask for the decision and the approver's name and role. Record both in the STATUS.md gate log and suggest a git tag (`sdlc/<slug>/G<n>`). A waiver records the accepted risk and who accepted it.
9. **After a baseline,** every change to an approved deliverable goes through a [change request](templates/change-request.md): RTM impact analysis → decision → update the affected deliverables → re-check the affected gates.

**Partial use.** If the user wants a single deliverable (e.g. "write the feature design for login"), produce just that one, following its phase's guidance. Mention any missing upstream inputs, but don't force the whole lifecycle.

Workspace layout in the target project:
```
docs/sdlc/<initiative-slug>/
├── STATUS.md               # phase, gate log, decisions, risks, CRs, open items
├── requirements.md         # Phase 1
├── rtm.md                  # Phases 1–6
├── architecture.md         # Phase 2 (threat model inside)
├── adr/NNNN-<decision>.md  # Phase 2 onwards
├── design/<feature>.md     # Phase 3
├── test-plan.md            # Phases 1–5 (+ test summary report)
├── release-checklist.md    # Phase 6
├── cr/CR-NNN-<title>.md    # after any baseline
└── postmortem/PM-NNN-<title>.md  # Phase 7, after each S1 incident
```

## File index
- **Phases:** [1 Requirements](phases/1-requirements.md) · [2 Architecture](phases/2-architecture.md) · [3 Detailed design](phases/3-detailed-design.md) · [4 Implementation](phases/4-implementation.md) · [5 Testing](phases/5-testing.md) · [6 Release](phases/6-release.md) · [7 Maintenance](phases/7-maintenance.md)
- **Reference:**
  - [architecture](reference/architecture.md): layers, module layouts, default stack, Gradle, DI, error model;
  - [code patterns](reference/code-patterns.md): canonical Kotlin for each layer;
  - [UI/UX](reference/ui-ux.md) · [security & privacy](reference/security-privacy.md) · [performance & reliability](reference/performance-reliability.md) · [testing](reference/testing.md) · [review checklist](reference/review-checklist.md).
- **Templates:** [status](templates/status.md) · [requirements](templates/requirements.md) · [architecture](templates/architecture.md) · [adr](templates/adr.md) · [feature-design](templates/feature-design.md) · [test-plan](templates/test-plan.md) · [release-checklist](templates/release-checklist.md) · [change-request](templates/change-request.md) · [rtm](templates/rtm.md) · [postmortem](templates/postmortem.md)

## Conventions
- **Requirement IDs.** `FR-nnn` for functional requirements. `NFR-<ATTR>-nn` for non-functional ones, where ATTR is one of PERF, REL, SEC, PRIV, A11Y, MAINT, TEST, COMPAT, OBS, I18N, SIZE.
- **Test IDs.** `UT-` unit, `IT-` integration, `UI-` Compose UI, `ST-` system/NFR, `AT-` acceptance.
- Commits, PRs, designs and tests cite these IDs.
- **Numbers marked "e.g."** are examples. The real targets are agreed in the requirements.
- **Versions.** Libraries are always the latest stable release, declared once in `gradle/libs.versions.toml`; this skill pins none. Play policy values (vitals thresholds, the target-SDK deadline) change, so check the current Play Console documentation.
