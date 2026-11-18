---
name: compose-multiplatform-sdlc
description: Waterfall lifecycle for an Android + iOS app or feature built with Kotlin Multiplatform and Compose Multiplatform (shared logic and UI) - requirements, architecture, detailed design, implementation, testing, Google Play and App Store release, maintenance - with phase gates, sign-offs, traceability and change control. Bundles KMP best practices (source sets, expect/actual vs interfaces, Clean Architecture + MVVM in commonMain, Compose Multiplatform + Material 3, Koin, Ktor, Room KMP, iOS/Swift interop, OWASP MASVS on both platforms, testing, performance, accessibility), canonical code patterns, a PR review checklist and deliverable templates. Use when planning, designing, building, testing or releasing a KMP/CMP app or feature for Android and iOS, when bringing an Android app to iOS, when writing those documents for a KMP project, or when the user mentions waterfall, SDLC, V-model or phase gates for a cross-platform Kotlin app.
---

# Compose Multiplatform SDLC (waterfall)

A gated, document-driven lifecycle for an app that ships to **Android and iOS from one Kotlin codebase**: domain, data, ViewModels and Compose UI live in `commonMain`, and thin platform layers do only what one OS can do. It also covers a feature in an existing KMP app. Each phase produces reviewed deliverables and ends at a gate. The next phase starts only after an explicit sign-off.

## Principles
- **Quality is designed in.** Each design phase writes the tests that later verify it (see the [V-model](#v-model)). Every NFR has a measurable target.
- **Traceable.** Every requirement has an ID that is carried into design, code, tests and the release ([RTM](templates/rtm.md)).
- **Gates are real.** A baselined deliverable changes only through a [change request](templates/change-request.md).
- **Share by default, go native on purpose.** Logic and UI are shared. Code is platform-specific only when an OS capability, a store rule or a measured UX gap requires it. Each such case is listed in the architecture's platform matrix ([platform integration](reference/platform-integration.md)).
- **Two platforms, one bar.** Every requirement, NFR, test and gate applies to both Android and iOS unless the requirement is tagged for one platform. "Works on Android" is not done.
- **Opinionated defaults, explicit deviations.** The [default stack](reference/architecture.md#default-stack) applies unless an ADR says otherwise.
- **Project rules win.** If the target repo has a `CLAUDE.md` or `.claude/rules/`, they override this skill's conventions. This skill still governs the process and the quality bars.
- **Proportionate depth.** A feature gets lighter documents than a new app; see [Tailoring](#tailoring).
- **Reviewable output.** Documents follow fixed templates. Code follows one [pattern per concern](reference/code-patterns.md). PRs are small and single-purpose ([review checklist](reference/review-checklist.md)).

## Lifecycle
| # | Phase | Key question | Main deliverables | Gate |
|---|---|---|---|---|
| 1 | [Requirements](phases/1-requirements.md) | What must the app do on each platform, and how well? | Requirements (brief, FRs with platform tags, NFRs per platform, permissions, data inventory, store constraints), acceptance outline, RTM | G1 Requirements baseline |
| 2 | [Architecture](phases/2-architecture.md) | How is the shared code structured, what stays native, and on which stack? | Architecture document with platform matrix, ADRs, threat model, master test plan | G2 Architecture baseline |
| 3 | [Detailed design](phases/3-detailed-design.md) | How is each feature built? | Feature designs (screens, state, contracts, schema, platform notes, PR plan), integration test cases | G3 Ready to build |
| 4 | [Implementation](phases/4-implementation.md) | Is it built right, on both platforms? | Code and tests, Android + iOS CI, release candidates for both | G4 Code complete |
| 5 | [Testing](phases/5-testing.md) | Does it meet the spec on real Android and iOS devices? | Test reports, UAT sign-off, test summary report | G5 Release readiness (go/no-go) |
| 6 | [Release](phases/6-release.md) | Is it live on Google Play and the App Store, and stable? | Release checklist, rollout record, handover | G6 Launch accepted |
| 7 | [Maintenance](phases/7-maintenance.md) | Does it stay healthy as Android, iOS, Kotlin and both stores change? | Health reviews, CRs, hotfixes, yearly platform updates | Mini-cycle per change |

## V-model
| Design phase | Verified in Phase 5 by | Test basis written in |
|---|---|---|
| 1 Requirements | Acceptance tests (UAT on the Play internal or closed track and on TestFlight) | Phase 1: acceptance outline |
| 2 Architecture | System and NFR tests on the Android and iOS device matrix: startup, smoothness, security, accessibility, offline, upgrade | Phase 2: master test plan |
| 3 Detailed design | Integration tests (Room, Ktor `MockEngine`, DI graph, navigation) and Compose UI tests run on both platforms | Phase 3: feature designs |
| 4 Implementation | Unit tests in `commonTest` (run on the JVM and the iOS simulator) and platform tests for `androidMain`/`iosMain` code | Phase 4: written with the code |

## Tailoring
| Deliverable | New app (or an Android app brought to iOS) | Feature in an existing KMP app |
|---|---|---|
| [Requirements](templates/requirements.md) | Full | Brief, feature FRs, changed NFRs, new permissions and data per platform |
| [Architecture](templates/architecture.md) | Full, with stack, module layout and platform matrix ADRs | Delta: changed modules, platform matrix rows, data flows and threats |
| [ADRs](templates/adr.md) | Stack deviations, module layout, iOS integration, other key choices | One per significant decision |
| [Feature design](templates/feature-design.md) | One per feature | One for the feature |
| [Test plan](templates/test-plan.md) | Master plan and summary report | Feature scope plus regression scope, on both platforms |
| [Release checklist](templates/release-checklist.md) | Full, both stores, with hypercare | Standard; rollout behind a feature flag |
| [STATUS](templates/status.md), [RTM](templates/rtm.md) | Required | Required (feature rows only) |

- **Bringing an existing Android app to iOS** is a new initiative: run the full lifecycle. Phase 2 adds a migration plan ([architecture: migration](reference/architecture.md#migrating-an-android-app-to-kmp)), and every migration step must still ship on Android on its own.
- A small feature may combine G2 and G3 into one review. **G5 is never skipped or combined**, and it covers both platforms.

## How Claude runs this workflow
1. **Workspace.** In the target project, open `docs/sdlc/<initiative-slug>/STATUS.md`. If it exists, resume at the phase it records. If not, create it from [templates/status.md](templates/status.md).
2. **Facts.** In an existing project, read:
   - `settings.gradle.kts`, `gradle/libs.versions.toml`, and the build files of the shared modules (targets, source sets, framework `baseName` and `isStatic`) and of `androidApp`;
   - the Xcode project in `iosApp/` (deployment target, bundle ID, the build phase that embeds the Kotlin framework), `Info.plist` and `PrivacyInfo.xcprivacy`;
   - `CLAUDE.md` and `.claude/rules/`.

   Record the modules, the targets, `minSdk`/`targetSdk`/`compileSdk`, the iOS deployment target, the Kotlin, Compose Multiplatform, AGP and Xcode versions, and the stack in STATUS.md. Don't contradict them without an ADR.
3. **Scope.** Confirm with the user:
   - new app, Android app brought to iOS, or feature;
   - platforms: Android and iOS, and whether desktop or web are explicitly out of scope (the default);
   - target users and devices on each platform;
   - compliance (e.g. GDPR, COPPA, HIPAA) and the MASVS level;
   - anything that must stay native (e.g. a widget, a watch app, an SDK without a KMP binding);
   - existing documents to reuse.

   Record the answers and pick the tailoring column.
4. **Load only what's needed:** the current phase file and the references its **Load** line lists. If STATUS.md doesn't show the previous gate as approved, stop and say so.
5. **Write the deliverables** from `templates/` into the workspace.
   - Mark unknowns `TBD-<n>` and assumptions `ASSUMPTION:`, and list them in STATUS.md.
   - Ask the user for what only stakeholders can decide: targets, priorities, approvers, platform parity.
   - Never invent requirements, numbers, approvals or sign-offs.
6. **Trace.** Add every new requirement, design element and test to `rtm.md`, with its platforms.
7. **Gate review.** Run the phase's exit checklist for both platforms. Present the deliverables and their status, the checklist results, open TBDs, top risks, and a recommendation: approve, approve with conditions, or rework.
8. **STOP for sign-off.** Ask for the decision and the approver's name and role. Record both in the STATUS.md gate log and suggest a git tag (`sdlc/<slug>/G<n>`). A waiver records the accepted risk and who accepted it.
9. **After a baseline,** every change to an approved deliverable goes through a [change request](templates/change-request.md): RTM impact analysis → decision → update the affected deliverables → re-check the affected gates.

**Partial use.** If the user wants a single deliverable (e.g. "write the feature design for login"), produce just that one, following its phase's guidance. Mention any missing upstream inputs, but don't force the whole lifecycle. The same goes for code: "add a notes screen to the shared module" uses the [code patterns](reference/code-patterns.md) and the [review checklist](reference/review-checklist.md) without the documents.

Workspace layout in the target project:
```
docs/sdlc/<initiative-slug>/
├── STATUS.md               # phase, platforms, gate log, decisions, risks, CRs, open items
├── requirements.md         # Phase 1
├── rtm.md                  # Phases 1–6
├── architecture.md         # Phase 2 (platform matrix and threat model inside)
├── adr/NNNN-<decision>.md  # Phase 2 onwards
├── design/<feature>.md     # Phase 3
├── test-plan.md            # Phases 1–5 (+ test summary report)
├── release-checklist.md    # Phase 6
└── cr/CR-NNN-<title>.md    # after any baseline
```

## File index
- **Phases:** [1 Requirements](phases/1-requirements.md) · [2 Architecture](phases/2-architecture.md) · [3 Detailed design](phases/3-detailed-design.md) · [4 Implementation](phases/4-implementation.md) · [5 Testing](phases/5-testing.md) · [6 Release](phases/6-release.md) · [7 Maintenance](phases/7-maintenance.md)
- **Reference:**
  - [architecture](reference/architecture.md): layers, source sets, module layouts, default stack, Gradle, DI, error model, threading, migrating an Android app;
  - [platform integration](reference/platform-integration.md): where code lives, expect/actual, platform services, the iOS app and Swift interop, lifecycle differences;
  - [code patterns](reference/code-patterns.md): canonical Kotlin (and the little Swift) for each layer;
  - [UI/UX](reference/ui-ux.md) · [security & privacy](reference/security-privacy.md) · [performance & reliability](reference/performance-reliability.md) · [testing](reference/testing.md) · [review checklist](reference/review-checklist.md).
- **Templates:** [status](templates/status.md) · [requirements](templates/requirements.md) · [architecture](templates/architecture.md) · [adr](templates/adr.md) · [feature-design](templates/feature-design.md) · [test-plan](templates/test-plan.md) · [release-checklist](templates/release-checklist.md) · [change-request](templates/change-request.md) · [rtm](templates/rtm.md)

## Conventions
- **Requirement IDs.** `FR-nnn` for functional requirements. `NFR-<ATTR>-nn` for non-functional ones, where ATTR is one of PERF, REL, SEC, PRIV, A11Y, MAINT, TEST, COMPAT, OBS, I18N, SIZE.
- **Test IDs.** `UT-` unit, `IT-` integration, `UI-` Compose UI, `ST-` system/NFR, `AT-` acceptance.
- **Platform tags.** A requirement, design element or test applies to both platforms unless it carries `[Android]` or `[iOS]`. NFR targets may differ per platform; then the NFR lists one target per platform.
- Commits, PRs, designs and tests cite these IDs.
- **Numbers marked "e.g."** are examples. The real targets are agreed in the requirements.
- **Versions.** Libraries are always the latest stable release, declared once in `gradle/libs.versions.toml`; this skill pins none. Kotlin, Compose Multiplatform, AGP and Xcode must be compatible with each other: check JetBrains' compatibility table before upgrading any of them. Store policy values (Play's target-SDK deadline, Apple's minimum Xcode/SDK for uploads, vitals thresholds, review guidelines) change, so check the current Play Console and App Store Connect documentation.
