# Phase 4: Implementation
**Gate:** G4 Code complete
**Deliverables:** code with unit tests, CI pipeline, release candidate (RC) build, RTM update
**Load:** [code-patterns](../reference/code-patterns.md), [architecture](../reference/architecture.md), [testing](../reference/testing.md), [review-checklist](../reference/review-checklist.md); for project setup, also [security-privacy](../reference/security-privacy.md) and [performance-reliability](../reference/performance-reliability.md)

## Goal
Build the app exactly as designed, in small reviewed PRs, with tests and quality gates from the first commit.

## Entry criteria
- G3 approved; feature designs and contracts frozen.
- The repository, a CI runner, and a test backend or mock server are available.

## Activities
### Step 0: project setup (new app only)
1. **Modules and build.**
   - Create the modules from the module-layout ADR, with convention plugins in `build-logic`.
   - Declare every dependency in `gradle/libs.versions.toml` at the latest stable version. No versions in module build files.
2. **Build config, in the convention plugins only.**
   - `minSdk`, `targetSdk`, `compileSdk`, the JVM toolchain and KSP.
   - For release: `isMinifyEnabled = true` and `isShrinkResources = true`.
3. **App foundations.**
   - The `@HiltAndroidApp` application class.
   - The Material 3 theme in the design-system module; edge-to-edge.
   - `network_security_config.xml` with cleartext traffic off.
   - `dataExtractionRules` that exclude sensitive files from backups.
4. **Debug-only tools:** StrictMode, LeakCanary, a Timber debug tree, HTTP logging.
5. **Quality tools:** ktlint, detekt, Android Lint (warnings as errors for new code), Kover.
6. **Process:** the CI pipeline below, branch protection on `main`, a PR template.
7. **Prove the pipeline.** Before writing features, merge one tiny vertical slice through it, e.g. a screen that reads from a fake repository.

### Feature build order
Each step is one or more PRs, taken from the feature design's slice plan. Building the domain first means every later PR builds on a reviewed, tested contract.
1. **Domain:** models, repository interfaces, UseCases, and unit tests (pure JVM).
2. **Data:**
   - DTOs, the API service, Room entities, DAOs and migrations, mappers;
   - the `…RepositoryImpl`;
   - tests using fakes, MockWebServer and in-memory Room.
3. **Presentation:**
   - `UiState` and the ViewModel, with tests;
   - stateless Composables with `@Preview`s;
   - the stateful screen.
4. **Wiring:** Hilt bindings, the navigation entry, the feature flag.
5. **Critical flow:** a Compose UI test for the Must stories.

### Coding rules
- Follow the [code patterns](../reference/code-patterns.md) and the project's own rules. Where they conflict, the project's rules win.
- Branch names, commits and PRs reference the ticket and the FR IDs.
- Keep the layers clean: no business logic in Composables, no repository in a ViewModel, no `android.*` in the domain.
- Hard-code nothing: no strings, colours, dimensions, URLs or secrets.
- Handle every error path in the design. Never swallow an exception.
- Add the analytics events and logs from the design. Never log PII or tokens.

### CI pipeline
Cheapest checks first. Any failure blocks the merge.
1. `./gradlew assembleDebug`
2. `./gradlew ktlintCheck detekt lint`
3. `./gradlew test`, plus the Kover coverage floor (e.g. ≥ 80% of lines in domain and ViewModels)
4. `./gradlew assembleRelease`, which proves the R8 rules and the release config
5. A dependency vulnerability scan and a secrets scan
6. On merge or nightly:
   - instrumented and screenshot tests;
   - Macrobenchmark for startup and the key scrolls, on a physical device or a device farm. Compare each result with its NFR budget and the last `main` run. Fail or flag the build when a budget is broken or a result regresses beyond an agreed margin (e.g. 10%);
   - distribute the build to testers (e.g. the Play internal track or Firebase App Distribution).

### Pull requests
- **Size and checks:**
  - ≤ ~400 changed lines;
  - one concern;
  - CI green;
  - at least one approving review against the [review checklist](../reference/review-checklist.md).
- **Description:**
  - what changed and why, with the FR IDs;
  - screenshots in light, dark and large font for UI changes.
- **Deviations** from the approved design or contract need a CR, not just a PR comment.
- **The owner's code review mode** (STATUS.md):
  - *Approve before writing:* present each PR's files, every line, with a plain explanation of what each part does and why. Write the code only after approval, then run the checks.
  - *Review after writing:* open the PR, then walk the owner through it before merging.

### Definition of Done (per PR)
- Code follows the patterns.
- New logic has tests, and new Composables have previews.
- Strings are in resources.
- CI is green and the PR is reviewed.
- The RTM row is updated.

## Exit checklist (G4)
- [ ] All in-scope FRs implemented and merged; feature flags set for the release
- [ ] CI green on the release branch; coverage floor met
- [ ] No open high or critical findings from lint, detekt, dependency or secrets scans, unless formally accepted
- [ ] All code reviewed; no unapproved deviations from the designs
- [ ] RC built by CI (signed, R8 on); mapping file archived; RC installed and smoke-tested
- [ ] Test environment, test accounts and test data ready; RTM updated

## Pitfalls
- **Building the UI first** against imagined data, then bending the domain to fit it.
- **Big-bang PRs** at the end of a feature.
- **Testing only debug builds.** R8 removes classes that reflection or serialization needs.
- **Suppressing lint or detekt warnings** to make CI pass.
- **"Temporary" API keys or URLs** in code.
