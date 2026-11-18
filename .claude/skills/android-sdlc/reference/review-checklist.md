# Review checklist

For authors before they ask for a review, and for reviewers. A PR that breaks the PR rules goes back to the author before anyone reviews it line by line.

## PR rules
- **Small and single-purpose.** One concern, ≤ ~400 changed lines (not counting generated files), taken from the feature design's slice plan.
- **Branch and title** follow the project's git rules, e.g. `feature/JIRA-123-notes-list` and `JIRA-123: Add notes list screen`.
- **The description** covers:
  - what changed and why;
  - the FR IDs;
  - how it was tested;
  - for UI changes, screenshots or a recording in light, dark and 200% font;
  - risks, and how to roll back (e.g. a feature flag).
- **CI is green before review,** and the PR has no unrelated reformatting.

## Review order
Feature design → tests (do they describe the right behaviour?) → domain → data → presentation → resources and build files.

## Checklist
**Scope and traceability**
- [ ] Matches the approved feature design; nothing unrequested; any deviation has an approved CR
- [ ] FR IDs in the PR; RTM row updated

**Architecture**
- [ ] Layer rules hold: no `android.*` in the domain; ViewModels call UseCases only; DTOs and entities stay in the data layer
- [ ] Code sits in the right module and package; no feature-to-feature dependency
- [ ] Dependencies are injected: no `object` singletons holding state, no services constructed by hand

**Kotlin**
- [ ] `val` and read-only public types; no `!!`; `when` over a sealed type lists every subtype, with no `else`
- [ ] Clear names, small functions, no magic numbers, no dead or commented-out code

**Coroutines and Flow**
- [ ] No `GlobalScope`, `runBlocking` or hard-coded `Dispatchers` in production code
- [ ] `CancellationException` never swallowed; work is cancelled with its scope; CPU loops call `ensureActive()`
- [ ] Shared mutable state guarded by a `Mutex` or `MutableStateFlow.update`; cleanup after cancellation in `NonCancellable`
- [ ] `StateFlow` exposed read-only and built with `stateIn(… WhileSubscribed …)`; the UI collects with `collectAsStateWithLifecycle`

**Compose UI**
- [ ] A stateful `…Screen` wraps a stateless `…Content`; no business logic or navigation decisions in Composables
- [ ] Every `UiState` is rendered, including loading, empty, error and offline
- [ ] Strings, colors and sizes come from resources or design tokens
- [ ] `modifier: Modifier = Modifier` is the first optional parameter; lazy lists have keys
- [ ] Previews for each state, in light and dark

**Data**
- [ ] Network calls return `AppResult`; errors are mapped at the boundary
- [ ] Observable DAO queries return `Flow`
- [ ] A schema change comes with a migration, a migration test and the exported schema
- [ ] Cache and sync behaviour matches the design

**Security and privacy**
- [ ] No secrets, tokens or PII in code, logs, analytics or crash reports
- [ ] Input from intents, deep links and the network is validated; new components aren't exported
- [ ] Any new permission or SDK is approved in the design, with a rationale and its Data safety impact

**Tests**
- [ ] New logic has unit tests for the happy path, each error and the edge cases
- [ ] Tests use fakes and are deterministic
- [ ] A bug fix includes a test that failed before the fix

**Performance, accessibility, i18n, observability**
- [ ] No I/O or heavy work on the main thread; no Context leaks
- [ ] Content descriptions, 48 dp touch targets, works at 200% font, RTL-safe
- [ ] The analytics events and logs from the design are present and free of PII

## Giving feedback
- **Label each comment:** **blocker** (must fix), **suggestion** (optional), **question**, or **nit**.
- **Explain why,** and link the rule or pattern.
- **Approve once the blockers are fixed.** Don't hold a PR for nits.
