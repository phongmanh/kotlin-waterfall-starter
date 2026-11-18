# Phase 3: Detailed design
**Gate:** G3 Ready to build
**Deliverables:** one [feature design](../templates/feature-design.md) per feature (`design/<feature>.md`), integration test cases, RTM update
**Load:** [code-patterns](../reference/code-patterns.md), [ui-ux](../reference/ui-ux.md), [testing](../reference/testing.md)

## Goal
Specify each feature precisely enough that any Android developer can build it without guessing, and a reviewer can check the code against it.

## Entry criteria
- G2 approved; the architecture and ADRs are baselined.
- UI designs (e.g. Figma) exist for the features in scope, or there's a decision to use standard Material 3 layouts.
- Backend contracts exist, at least as a draft OpenAPI spec.

## Activities
Fill in the template for each feature:
1. **Screens.** List the screens with their design links. For each screen, define:
   - its `UiState` in Kotlin: a sealed interface with Loading, Success and Error, plus Empty if the content can be empty;
   - the user actions (`onAction`) and one-off events (e.g. a snackbar);
   - its route and arguments;
   - what must survive process death (`SavedStateHandle`).
2. **Domain.** Models, UseCase signatures (one business action each) and repository interfaces. Write them as Kotlin signatures, not prose.
3. **Data.**
   - Endpoints: method, path, request, response, error codes.
   - DTOs and their mappers (`toDomain()`, `toEntity()`).
   - Room entities, DAO queries (observable queries return `Flow`), indices, and the migration from the previous schema version.
   - DataStore keys, and what is encrypted.
   - The cache and refresh policy, following the architecture's data strategy.
4. **Errors.** A table mapping each `AppError` to a string resource and a UI behaviour: retry, re-login, or an inline field error.
5. **Analytics.** Events and parameters from the tracking plan, with no PII.
6. **Accessibility and i18n.**
   - Content descriptions, headings, focus order, custom actions.
   - New strings and plurals.
   - RTL concerns.
7. **Test cases.** Integration (`IT-`) and Compose UI (`UI-`) cases, each traced to an FR. Unit tests are written with the code in Phase 4.
8. **PR slice plan.** Split the work into small, reviewable PRs that follow the [build order](4-implementation.md#feature-build-order). Each PR has a one-line goal and stays at or below ~400 changed lines.
9. **Review.** Walk through each design with the tech lead and another Android developer. QA reviews the test cases; the designer reviews the UI states.

## Exit checklist (G3)
- [ ] Every in-scope FR is covered by a feature design
- [ ] Every screen has its full `UiState`, actions and events, including empty, error and offline states
- [ ] UseCase, repository and DAO signatures written in Kotlin
- [ ] Endpoints and Room schema frozen; migrations designed; mock server or fakes available
- [ ] Error-to-message table complete; new strings listed
- [ ] `IT-` and `UI-` test cases traced to FRs; RTM updated
- [ ] PR slice plan agreed; estimates fit the schedule
- [ ] Designs reviewed and approved; baseline tagged

## Pitfalls
- **Designing only the Success state.** Most bugs live in Loading, Empty, Error and Offline.
- **Prose instead of signatures.** "The screen loads the user" hides the error-handling and threading decisions.
- **A schema change without a migration plan.**
- **One giant PR per feature,** which nobody can review well.
