# Phase 4: Implementation
**Gate:** G4 Code complete
**Deliverables:** code with tests, CI pipeline for both platforms, release candidate (RC) builds for Android and iOS, RTM update
**Load:** [code-patterns](../reference/code-patterns.md), [architecture](../reference/architecture.md), [platform-integration](../reference/platform-integration.md), [testing](../reference/testing.md), [review-checklist](../reference/review-checklist.md); for project setup, also [security-privacy](../reference/security-privacy.md) and [performance-reliability](../reference/performance-reliability.md)

## Goal
Build the app exactly as designed, in small reviewed PRs, with tests and quality gates for both platforms from the first commit.

## Entry criteria
- G3 approved; feature designs and contracts frozen.
- The repository, Linux and macOS CI runners, both store accounts, and a test backend or mock server are available.

## Activities
### Step 0: project setup (new app only)
1. **Modules and build.**
   - Create `androidApp`, `iosApp`, the shared module(s) from the module-layout ADR, and `build-logic` with convention plugins.
   - Declare every dependency in `gradle/libs.versions.toml` at the latest stable version, with Kotlin, Compose Multiplatform, AGP and Xcode compatible. No versions in module build files.
2. **Build config, in the convention plugins only.**
   - Targets (Android, `iosArm64`, `iosSimulatorArm64`), the static framework and its `baseName`, `compileSdk`, `minSdk`, the JVM toolchain and KSP for every target.
   - `androidApp`: `targetSdk`; for release, `isMinifyEnabled = true` and `isShrinkResources = true`.
   - `iosApp`: the deployment target, the `embedAndSignAppleFrameworkForXcode` build phase, `.xcconfig` files per configuration.
3. **App foundations.**
   - `AppConfig` built by each entry point; Koin started once on each platform.
   - The Material 3 theme in the design-system module; edge-to-edge and safe areas on both platforms.
   - Android: `network_security_config.xml` with cleartext traffic off; `dataExtractionRules` that exclude sensitive files from backups.
   - iOS: App Transport Security on; `Info.plist` usage descriptions and `CFBundleLocalizations`; entitlements; `PrivacyInfo.xcprivacy`; app icon and launch screen.
4. **Debug-only tools:** Kermit debug output, Ktor logging with sanitised headers; StrictMode and LeakCanary on Android; the Main Thread Checker and memory graph on iOS.
5. **Quality tools:** ktlint, detekt (all source sets), Android Lint (warnings as errors for new code), SwiftLint, Kover.
6. **Process:** the CI pipeline below, branch protection on `main`, a PR template that asks for both platforms.
7. **Prove the pipeline.** Before writing features, merge one tiny vertical slice through it and run it on both platforms, e.g. a screen in `commonMain` that reads from a fake repository, built and launched on an Android emulator and an iOS simulator.

### Feature build order
Each step is one or more PRs, taken from the feature design's slice plan. Building the domain first means every later PR builds on a reviewed, tested contract.
1. **Domain:** models, repository interfaces, UseCases, and `commonTest` tests.
2. **Data:**
   - DTOs, the Ktor API, Room entities, DAOs and migrations, mappers;
   - the `…RepositoryImpl`;
   - tests using fakes, `MockEngine` and an in-memory Room database.
3. **Platform implementations** from the platform notes: `androidMain`, `iosMain` or Swift, each with tests on its platform.
4. **Presentation:**
   - `UiState` and the ViewModel, with tests;
   - stateless Composables with `@Preview`s;
   - the stateful screen.
5. **Wiring:** Koin modules (and the DI graph test), the navigation entry, the feature flag, Swift glue if any.
6. **Critical flow:** a common Compose UI test for the Must stories, run on both platforms.

### Coding rules
- Follow the [code patterns](../reference/code-patterns.md) and the project's own rules. Where they conflict, the project's rules win.
- Branch names, commits and PRs reference the ticket and the FR IDs.
- Keep the layers clean: no business logic in Composables, no repository in a ViewModel, no platform types in the domain.
- Keep platform code thin: interfaces and `expect` functions, never business logic in an `actual`.
- Hard-code nothing: no strings, colours, dimensions, URLs or secrets.
- Handle every error path in the design. Never swallow an exception, and never let one escape into Swift.
- Add the analytics events and logs from the design. Never log PII or tokens.
- **Run it on both platforms before the PR.** A change to shared UI is checked on an iOS simulator, not only in previews.

### CI pipeline
Cheapest checks first. Any failure blocks the merge.
1. **Linux:** `./gradlew :androidApp:assembleDebug`
2. **Linux:** `./gradlew ktlintCheck detekt :androidApp:lint`
3. **Linux:** `./gradlew :shared:allTests` (the JVM run of `commonTest` and Android host tests), plus the Kover coverage floor (e.g. ≥ 80% of lines in domain and ViewModels)
4. **macOS:**
   - `./gradlew :shared:iosSimulatorArm64Test`;
   - `xcodebuild … build` of `iosApp` for the simulator;
   - SwiftLint.
5. **Release configs:** `./gradlew :androidApp:assembleRelease` (proves R8 rules) and an `xcodebuild archive` with the Release configuration (proves the release framework and signing set-up).
6. A dependency vulnerability scan (Gradle and iOS dependencies) and a secrets scan.
7. On merge or nightly:
   - common Compose UI tests on an Android emulator and the iOS simulator; screenshot tests;
   - distribute builds to testers: the Play internal track or Firebase App Distribution, and TestFlight.

### Pull requests
- **Size and checks:**
  - ≤ ~400 changed lines;
  - one concern;
  - CI green for both platforms;
  - at least one approving review against the [review checklist](../reference/review-checklist.md); an iOS-aware reviewer for iOS files.
- **Description:**
  - what changed and why, with the FR IDs;
  - screenshots from Android and iOS, in light, dark and large font, for UI changes.
- **Deviations** from the approved design or contract need a CR, not just a PR comment.

### Definition of Done (per PR)
- Code follows the patterns.
- New logic has tests that pass on the JVM and the iOS simulator; new Composables have previews.
- Strings are in `composeResources`.
- The app builds and runs on both platforms.
- CI is green and the PR is reviewed.
- The RTM row is updated.

## Exit checklist (G4)
- [ ] All in-scope FRs implemented and merged on both platforms; feature flags set for the release
- [ ] CI green on the release branch for Android and iOS; coverage floor met
- [ ] No open high or critical findings from lint, detekt, SwiftLint, dependency or secrets scans, unless formally accepted
- [ ] All code reviewed; no unapproved deviations from the designs or the platform matrix
- [ ] Android RC built by CI (signed AAB, R8 on), mapping file archived
- [ ] iOS RC built by CI (Release configuration, distribution-signed), dSYMs archived, uploaded to TestFlight
- [ ] Both RCs installed and smoke-tested on real devices
- [ ] Test environment, test accounts and test data ready; RTM updated

## Pitfalls
- **"iOS last":** building everything on Android and discovering iOS layout, performance and lifecycle issues at the end.
- **Building the UI first** against imagined data, then bending the domain to fit it.
- **Big-bang PRs** at the end of a feature.
- **Testing only debug builds.** R8 removes classes that reflection or serialization needs; a debug Kotlin/Native framework hides real iOS performance.
- **A growing public API** in shared modules, which bloats the iOS header and build time.
- **Suppressing lint, detekt or SwiftLint warnings** to make CI pass.
- **"Temporary" API keys or URLs** in code, `Info.plist` or committed `.xcconfig` files.
