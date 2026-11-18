# Phase 2: Architecture
**Gate:** G2 Architecture baseline
**Deliverables:** [architecture document](../templates/architecture.md) (threat model inside), [ADRs](../templates/adr.md), master [test plan](../templates/test-plan.md), RTM update
**Load:** [architecture](../reference/architecture.md), [security-privacy](../reference/security-privacy.md), [performance-reliability](../reference/performance-reliability.md), [testing](../reference/testing.md)

## Goal
Decide how the app is structured to meet the requirements, especially the NFRs, and fix the stack. Every feature is then designed against the same rules.

## Entry criteria
- G1 approved; the requirements and RTM are baselined.
- The top 3–5 quality goals are ranked (e.g. offline > startup > security).

## Activities
1. **Drivers.**
   - Turn the top NFRs into scenarios, e.g. "On a low-end phone with no network, opening a saved note takes ≤ 1 s."
   - Map each scenario to a tactic, e.g. Room as the single source of truth.
2. **Stack.**
   - Start from the [default stack](../reference/architecture.md#default-stack). Write an ADR only for a deviation or an open choice, e.g. the analytics vendor, or Navigation 3 vs Navigation Compose.
   - Confirm the backend contract format; OpenAPI is preferred.
3. **Module layout.** Apply the [size rule](../reference/architecture.md#module-layout): layer modules, or `feature:*` + `core:*` modules. Record the choice in an ADR and draw the module graph.
4. **Layer rules.**
   - Adopt the [layer rules](../reference/architecture.md#layers) and list any project-specific additions.
   - Enforce them in review, and with a Gradle dependency check or a detekt rule where possible.
5. **Data strategy, per repository.** Decide and record:
   - the source of truth: Room, DataStore, or network only;
   - the cache policy and what triggers a refresh;
   - sync through WorkManager, and the conflict policy;
   - the Room migration policy;
   - what is encrypted.

   See [reliability](../reference/performance-reliability.md#reliability).
6. **API integration.**
   - Base URLs per build type.
   - Auth and token refresh.
   - The error model, pagination and API versioning.
   - The **minimum supported app version**, and the forced-update path.
7. **Navigation.** A graph per feature, type-safe routes, deep links through verified App Links, and the back behaviour.
8. **Cross-cutting decisions.**
   - DI scopes and dispatchers.
   - The `AppError` model and how it maps to user messages.
   - Logging without PII.
   - Feature flags and remote config.
   - i18n.
   - The design-system module.
9. **Threat model.**
   - List the assets: tokens, PII, payments.
   - List the entry points: UI, deep links, intents, network, backups, SDKs.
   - Apply STRIDE to each entry point.
   - Map each mitigation to a MASVS control and a requirement ID.
10. **Observability.**
    - Crash and ANR reporting; performance monitoring.
    - The analytics tracking plan, with consent.
    - A release-health dashboard.
11. **Build and delivery.**
    - Build types (debug, release); flavors only if environments need them.
    - Signing: Play App Signing, with the upload key in CI secrets.
    - CI stages, as in [Phase 4](4-implementation.md#ci-pipeline).
    - Release tracks.
12. **Test strategy.** The master test plan covers:
    - test levels and tools;
    - the device matrix: `minSdk`, the latest Android, low-RAM, tablet, foldable, popular OEMs;
    - test data and environments (mock server, staging);
    - entry and exit criteria per level.
13. **Proofs of concept.** For each risky unknown, run a time-boxed, throwaway spike. Examples: background sync on OEMs with aggressive battery saving, or a heavy SDK's startup cost. Record the outcome in the ADR.
14. **Review.** Walk each driver scenario through the design with the tech lead, a senior Android developer, QA and security.

## Exit checklist (G2)
- [ ] Each NFR maps to a tactic; driver scenarios walked through
- [ ] Stack deviations and module layout recorded in accepted ADRs
- [ ] Data strategy defined for every repository: source of truth, sync, conflicts, migrations
- [ ] Minimum supported app version and forced-update path defined
- [ ] Threat model reviewed; mitigations mapped to MASVS controls and requirement IDs
- [ ] Observability, CI/CD and release tracks defined
- [ ] Master test plan with the device matrix approved
- [ ] Risky unknowns retired by a PoC or formally accepted
- [ ] RTM updated; baseline tagged

## Pitfalls
- **Adding libraries "because everyone uses them"** instead of because a requirement needs them.
- **Wrong module granularity:** many modules before there are features to fill them, or one giant `app` module for a 20-feature app.
- **No offline or conflict policy** until users lose data.
- **Forgetting old app versions,** which keep calling the API for months.
- **Treating the threat model as paperwork.** Every mitigation must become a requirement or a design element.
