# Phase 3: Detailed design
**Gate:** G3 Ready to build
**Deliverables:** one [feature design](../templates/feature-design.md) per feature (`design/<feature>.md`), integration test cases, RTM update
**Load:** [code-patterns](../reference/code-patterns.md), [platform-integration](../reference/platform-integration.md), [ui-ux](../reference/ui-ux.md), [testing](../reference/testing.md)

## Goal
Specify each feature precisely enough that any Kotlin developer can build it for both platforms without guessing, and a reviewer can check the code against it.

## Entry criteria
- G2 approved; the architecture, platform matrix and ADRs are baselined.
- UI designs (e.g. Figma) exist for the features in scope, including the agreed iOS adaptations, or there's a decision to use standard Material 3 layouts.
- Backend contracts exist, at least as a draft OpenAPI spec.

## Activities
Fill in the template for each feature:
1. **Screens.** List the screens with their design links. For each screen, define:
   - its `UiState` in Kotlin: a sealed interface with Loading, Success and Error, plus Empty if the content can be empty, and Pending if local changes can wait for sync;
   - the user actions (`onAction`) and one-off events (e.g. a snackbar);
   - its route, arguments and back affordance;
   - what must survive Android process death (`SavedStateHandle`) and what must survive iOS termination (local storage).
2. **Domain.** Models, UseCase signatures (one business action each) and repository interfaces. Write them as Kotlin signatures, not prose.
3. **Data.**
   - Endpoints: method, path, request, response, error codes.
   - DTOs and their mappers (`toDomain()`, `toEntity()`).
   - Room entities, DAO queries (`suspend` or `Flow`), indices, and the migration from the previous schema version.
   - DataStore keys, and what goes through the `SecureStore`.
   - The cache and refresh policy, following the architecture's data strategy.
4. **Platform notes.** For each platform-specific part of the feature:
   - the common interface or `expect` signature;
   - the Android and the iOS implementation, and where each lives (`androidMain`, `iosMain`, Swift in `iosApp`);
   - permissions and usage descriptions;
   - iOS-specific UI adaptations from the look-and-feel ADR.

   If a platform matrix row is new or changes, the architecture needs a CR.
5. **Errors.** A table mapping each `AppError` to a string resource and a UI behaviour: retry, re-login, or an inline field error.
6. **Analytics.** Events and parameters from the tracking plan, with no PII, sent through the common tracker.
7. **Accessibility and i18n.**
   - Content descriptions, headings, focus order, custom actions.
   - New strings and plurals in `composeResources`.
   - Locale-aware formatting; RTL concerns.
8. **Test cases.** Integration (`IT-`) and Compose UI (`UI-`) cases, each traced to an FR and tagged with the platforms it runs on. Unit tests are written with the code in Phase 4.
9. **PR slice plan.** Split the work into small, reviewable PRs that follow the [build order](4-implementation.md#feature-build-order). Each PR has a one-line goal and stays at or below ~400 changed lines. Platform implementations get their own PRs.
10. **Review.** Walk through each design with the tech lead and another developer; an iOS developer reviews the platform notes. QA reviews the test cases; the designer reviews the UI states on both platforms.

## Exit checklist (G3)
- [ ] Every in-scope FR is covered by a feature design
- [ ] Every screen has its full `UiState`, actions, events and back affordance, including empty, error, offline and pending states
- [ ] UseCase, repository and DAO signatures written in Kotlin
- [ ] Platform notes complete; platform interfaces and `expect` signatures written; matrix changes have a CR
- [ ] Endpoints and Room schema frozen; migrations designed; mock server or fakes available
- [ ] Error-to-message table complete; new strings listed
- [ ] `IT-` and `UI-` test cases traced to FRs and platforms; RTM updated
- [ ] PR slice plan agreed; estimates fit the schedule
- [ ] Designs reviewed and approved; baseline tagged

## Pitfalls
- **Designing only the Success state.** Most bugs live in Loading, Empty, Error, Offline and Pending.
- **Prose instead of signatures.** "The screen loads the user" hides the error-handling and threading decisions.
- **Leaving the iOS part for later.** "Platform notes: TBD" means the feature is half designed.
- **A schema change without a migration plan.**
- **One giant PR per feature,** which nobody can review well.
