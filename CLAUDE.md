# Project: <App Name>

<One or two sentences: what the app does, target platform.>

## Sessions and gates
- **Short sessions.** One unit of work per session (one deliverable draft, one feature design, one PR), then `/clear`. Before ending a session, update the deliverable and `docs/sdlc/<slug>/STATUS.md`, rewrite STATUS.md's `## Handoff` section (format in `.claude/rules/sdlc.md`), and tell the user: "Ready for `/clear`. The next session starts from the handoff."
- **Starting after `/clear`:** the `session-context.py` SessionStart hook injects the current phase, the next plan item and the handoff. Do its next action and load only what it lists; read documents by section (`grep -n '^##' <file>` first), not whole.
- **Cache inputs once.** External sources (backend contract, design, sibling repos) are fetched once into `docs/sdlc/<slug>/inputs/`, with source, version and commit in `inputs/README.md`; re-fetch only when the handoff says a source changed.
- **Baseline gate.** `guard-sdlc-baseline.py` asks before an edit to a deliverable that STATUS.md marks Approved. Only the user can switch it off, with `{ "env": { "SDLC_GATE": "off" } }` in the git-ignored `.claude/settings.local.json`. Never set it yourself, and never edit STATUS.md or the hooks to get past a gate.

## Architecture
- Clean Architecture + MVVM, strict unidirectional data flow.
- Calls flow `app` (presentation) → `domain` (business logic) → `data` (data sources). Dependencies point inward: `domain` is pure Kotlin and never imports from `app` or `data`; `data` implements the repository interfaces defined in `domain`.
- ViewModels call UseCases, never Repositories.

## Global Rules
- Kotlin only for new code (Java only in existing legacy modules); Hilt for DI; Coroutines + Flow for async — no RxJava or LiveData in new code.
- `val` over `var`; no `!!` — use `?.`, `?:` or `requireNotNull(x) { "reason" }`.
- Inject `CoroutineDispatcher`s; never hard-code `Dispatchers.IO`/`Default` outside DI modules.
- No hardcoded strings, colors or dimensions — use resources or design-system tokens; support dark mode.
- Every ViewModel, UseCase and Repository must be unit-testable by design.
- Follow SOLID, DRY, KISS, YAGNI.
- Fix ktlint/detekt/Lint warnings instead of suppressing them.
- Security: no secrets or API keys in source or version control; HTTPS only; store sensitive data in DataStore with keys in the Android Keystore (e.g. Tink) — `EncryptedSharedPreferences` is deprecated, don't use it; keep R8 obfuscation on for release builds.

## Before Finishing
Run `./gradlew ktlintCheck detekt test` and make sure it passes before calling a task done.
