# Phase 2: Architecture
**Gate:** G2 Architecture baseline
**Deliverables:** [architecture document](../templates/architecture.md) (platform matrix and threat model inside), [ADRs](../templates/adr.md), master [test plan](../templates/test-plan.md), RTM update
**Load:** [architecture](../reference/architecture.md), [platform-integration](../reference/platform-integration.md), [security-privacy](../reference/security-privacy.md), [performance-reliability](../reference/performance-reliability.md), [testing](../reference/testing.md)

## Goal
Decide how the shared code is structured to meet the requirements on both platforms, what stays native and why, and fix the stack. Every feature is then designed against the same rules.

## Entry criteria
- G1 approved; the requirements and RTM are baselined.
- The top 3–5 quality goals are ranked (e.g. offline > startup > security).

## Activities
1. **Drivers.**
   - Turn the top NFRs into scenarios per platform, e.g. "On the reference iPhone with no network, opening a saved note takes ≤ 1 s."
   - Map each scenario to a tactic, e.g. Room as the single source of truth.
2. **Stack.**
   - Start from the [default stack](../reference/architecture.md#default-stack). Write an ADR only for a deviation or an open choice, e.g. Koin vs compile-time DI, Navigation Compose vs Navigation 3, the crash reporter.
   - Record the Kotlin, Compose Multiplatform, AGP and Xcode versions, and check they're compatible.
   - Confirm the backend contract format; OpenAPI is preferred.
3. **Module layout.** Apply the [size rule](../reference/architecture.md#module-layout): one `shared` module, or `feature:*` + `core:*` modules behind an umbrella. Record the choice in an ADR and draw the module graph, including `androidApp` and `iosApp`.
4. **Platform matrix.** For each requirement that touches the OS (storage, background work, push, sign-in, permissions, deep links, payments, native views), decide:
   - shared, or platform-specific;
   - if platform-specific: the common interface, the Android implementation, the iOS implementation (Kotlin in `iosMain`, or Swift in `iosApp`) and why it can't be shared.

   Follow [where code lives](../reference/platform-integration.md#where-code-lives). Each row needs a test on its platform.
5. **iOS integration.** In an ADR:
   - how the framework is built and embedded (default: a static framework and the `embedAndSignAppleFrameworkForXcode` build phase);
   - the Swift surface: entry points and Swift implementations, and whether SKIE is needed;
   - which components adapt to iOS conventions ([platform look and feel](../reference/platform-integration.md#platform-look-and-feel)).
6. **Layer rules.**
   - Adopt the [layer rules](../reference/architecture.md#layers) and list any project-specific additions.
   - Enforce them in review, and with a Gradle dependency check or a detekt rule where possible.
7. **Data strategy, per repository.** Decide and record:
   - the source of truth: Room, DataStore, or network only;
   - the cache policy and what triggers a refresh;
   - sync through the `SyncScheduler`, what happens on iOS when background time never comes, and the conflict policy;
   - the Room migration policy;
   - what is encrypted, and where (`SecureStore`, file protection).

   See [reliability](../reference/performance-reliability.md#reliability).
8. **API integration.**
   - Base URLs per environment, delivered through `AppConfig` on both platforms.
   - Auth and token refresh.
   - The error model, pagination and API versioning.
   - The **minimum supported app version per platform**, and the forced-update path on each.
9. **Navigation.** A graph per feature, type-safe routes, deep links through App Links and Universal Links into one common router, and the back behaviour on each platform.
10. **Cross-cutting decisions.**
    - DI modules and scopes; how Koin starts on each platform; dispatchers.
    - The `AppError` model and how it maps to string resources.
    - Logging without PII.
    - Feature flags and remote config, shared by both apps.
    - i18n, including locale-aware formatting and `CFBundleLocalizations`.
    - The design-system module and its platform adaptations.
11. **Threat model.**
    - List the assets: tokens, PII, payments.
    - List the entry points per platform: UI, deep links, URL schemes, intents, push, network, backups, SDKs.
    - Apply STRIDE to each entry point.
    - Map each mitigation to a MASVS control, a platform and a requirement ID.
12. **Observability.**
    - Crash, ANR and hang reporting on both platforms, with readable Kotlin stack traces on iOS.
    - Performance monitoring.
    - The analytics tracking plan, with consent and ATT.
    - A release-health dashboard per platform.
13. **Build and delivery.**
    - Android build types; iOS Xcode configurations; flavors or schemes only if environments need them.
    - Signing: Play App Signing with the upload key in CI secrets; Apple distribution certificate and provisioning profiles in CI secrets.
    - CI: Linux runners for Android and common checks, macOS runners for iOS; stages as in [Phase 4](4-implementation.md#ci-pipeline).
    - Version numbering shared by both apps.
    - Release paths: Play tracks; TestFlight and App Store phased release.
14. **Test strategy.** The master test plan covers:
    - test levels, tools and the source sets they run in;
    - the device matrix: `minSdk` and the oldest supported iOS, the latest of each, low-RAM devices, Android tablet and foldable, iPad, popular OEMs;
    - test data and environments (mock server, staging);
    - entry and exit criteria per level.
15. **Proofs of concept.** For each risky unknown, run a time-boxed, throwaway spike on both platforms. Typical KMP spikes:
    - the heaviest screen in Compose on the reference low-end iPhone (scroll smoothness, startup);
    - each interop view (map, camera, web view);
    - background sync on iOS and on OEMs with aggressive battery saving;
    - an SDK with no KMP artifact, called through a Swift implementation;
    - the iOS app size with all planned dependencies.

    Record each outcome in its ADR.
16. **Review.** Walk each driver scenario through the design with the tech lead, a senior Android developer, a senior iOS developer, QA and security.

## Exit checklist (G2)
- [ ] Each NFR maps to a tactic on each platform; driver scenarios walked through
- [ ] Stack deviations, module layout and iOS integration recorded in accepted ADRs; toolchain versions compatible
- [ ] Platform matrix complete: every platform-specific capability has an interface, two implementations and a test plan
- [ ] Data strategy defined for every repository: source of truth, sync (including iOS background limits), conflicts, migrations
- [ ] Minimum supported app version and forced-update path defined for each platform
- [ ] Threat model reviewed; mitigations mapped to MASVS controls, platforms and requirement IDs
- [ ] Observability, CI/CD for both platforms, signing and release paths defined
- [ ] Master test plan with both device matrices approved
- [ ] Risky unknowns retired by a PoC on both platforms or formally accepted
- [ ] RTM updated; baseline tagged

## Pitfalls
- **Sharing too little:** ViewModels or UI kept per platform "to be safe", which doubles the work and the bugs.
- **Sharing too much:** forcing an iOS-only capability into common code with `if (platform…)` branches.
- **Choosing libraries without an iOS story,** then wrapping them in `expect`/`actual` everywhere.
- **Validating Compose on iOS only on a new iPhone** in a debug build.
- **No offline or conflict policy for iOS,** where background sync may never run.
- **Several Kotlin frameworks in the iOS app,** each with its own runtime.
- **Forgetting old app versions,** which keep calling the API for months on both platforms.
- **Treating the threat model as paperwork.** Every mitigation must become a requirement or a design element.
