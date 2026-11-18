# Architecture reference

Clean Architecture + MVVM with unidirectional data flow. The canonical code for each piece is in [code-patterns.md](code-patterns.md).

## Layers
```
presentation (Compose UI, ViewModel) ──▶ domain (UseCases, models, repository interfaces) ◀── data (RepositoryImpl, API, Room, DataStore)
```
- **Domain is pure Kotlin.** No `android.*`, Compose, Retrofit or Room types. It owns the models, the repository interfaces and the error model. `javax.inject` and `kotlinx.coroutines` are allowed.
- **Data implements the domain's repository interfaces.** DTOs and entities never leave the data layer; they are mapped with `toDomain()`.
- **Presentation depends on the domain only.**
  - A ViewModel calls UseCases, never repositories.
  - Composables render state and forward events. They hold no business logic.
- **Data flows one way.** State goes down as `StateFlow<UiState>`; events come up through `onAction`. Each screen has exactly one immutable `UiState`.
- **Dependencies point inward.** Hilt binds the implementations to the interfaces.

## Module layout
Choose one layout in a Phase 2 ADR.

**A. Layer modules**, for small apps:
```
app/      # Application, MainActivity, NavHost, DI root, ui/<feature>/ (screens + ViewModels)
domain/   # pure Kotlin/JVM: <feature>/model, <feature>/usecase, repository interfaces, AppError
data/     # Android library: <feature>/remote, <feature>/local, <feature>/repository, di/
```

**B. Feature + core modules**, for growing apps:
```
app/                    # Application, MainActivity, top-level NavHost, DI root
feature/<name>/         # screens, ViewModels, feature-only UseCases
core/model/             # domain models, AppError (pure Kotlin)
core/domain/            # shared UseCases, repository interfaces (pure Kotlin)
core/data/              # RepositoryImpl, mappers, DI bindings
core/network/  core/database/  core/datastore/
core/designsystem/      # theme, tokens, base components
core/ui/                # shared screen-level components and helpers
core/testing/           # fakes, test rules, test-data builders
build-logic/            # convention plugins
```
In layout B, features never depend on other features. They connect through navigation routes and core modules.

**Size rule.** Choose B if any of these hold; otherwise choose A:
- more than ~5 features are planned;
- more than ~3 developers, or 2+ teams;
- build times already hurt;
- Play Feature Delivery is needed;
- code will be shared with another app.

In either layout, **package by feature inside each module** (`…/notes/`, `…/settings/`). That keeps a later move from A to B mechanical.

## Default stack
Always use the latest stable versions, declared in `gradle/libs.versions.toml`. A deviation needs an ADR.

| Concern | Default | Notes |
|---|---|---|
| Language | Kotlin (K2 compiler) | No new Java |
| Build | Gradle Kotlin DSL, version catalog, convention plugins in `build-logic` | No versions or repeated config in module scripts |
| Annotation processing | KSP | Not kapt |
| UI | Jetpack Compose + Material 3 | Views only in legacy screens |
| Navigation | Navigation Compose with type-safe `@Serializable` routes | Navigation 3 is an option for new apps; decide in an ADR |
| DI | Hilt | Constructor injection everywhere |
| Async | Coroutines + Flow | No RxJava; no `GlobalScope` |
| Network | Retrofit + OkHttp + kotlinx.serialization | Ktor client via ADR (e.g. for Kotlin Multiplatform) |
| Database | Room | Schemas exported to `schemas/` and committed |
| Key-value storage | DataStore (Preferences or Proto) | Not `SharedPreferences` |
| Background work | WorkManager | For deferrable work that must run |
| Images | Coil | |
| Paging | Paging 3 | For lists that can grow |
| Logging | Timber | Debug tree in debug builds only |
| Crash and performance | Firebase Crashlytics + Performance, or an equivalent chosen by ADR | Mapping files uploaded by CI |
| Sign-in | Credential Manager; OAuth 2 + PKCE via Custom Tabs (e.g. AppAuth) | |
| Secure storage | Android Keystore + Tink | `EncryptedSharedPreferences` is deprecated |
| App integrity | Play Integrity API | Verdict checked on the server |
| Updates | Play In-App Updates | For forced updates |
| Static analysis | ktlint, detekt, Android Lint | |
| Testing | JUnit, kotlinx-coroutines-test, Turbine, fakes, Compose UI test, Roborazzi or Compose Preview Screenshot Testing | MockK sparingly; Robolectric only where needed. See [testing.md](testing.md) |
| Performance tools | Baseline Profiles, Macrobenchmark, LeakCanary (debug) | |
| Coverage | Kover | |

## Gradle conventions
- **One place for shared config.** `minSdk`, `targetSdk`, `compileSdk`, the JVM toolchain and Compose options live only in convention plugins.
- **Release builds** set `isMinifyEnabled = true` and `isShrinkResources = true`. Keep R8 keep-rules next to the code that needs them, in each module's `consumer-rules.pro`.
- **Config per build type** goes through `BuildConfig` fields (base URL, flag defaults).
  - Secrets come from `local.properties` or CI environment variables (e.g. via the Secrets Gradle Plugin), never from Git.
  - Anything in the APK is public, so real secrets stay on the server.
- **Build speed:** enable the build cache and the configuration cache.
- **Dependency scope:** use `api` only when a type is part of the module's public API; otherwise `implementation`.
- **Visibility:** mark everything `internal` unless another module uses it.

## Dependency injection
- **Scopes:**
  - `@Singleton` for OkHttp/Retrofit, the Room database and DAOs, DataStore and repositories.
  - Most UseCases are unscoped.
- **Bindings:** `@Binds` connects an interface to its implementation. `@Provides` is only for third-party builders (Retrofit, Room).
- **Dispatchers** are injected with qualifiers (`@IoDispatcher`, `@DefaultDispatcher`) so tests can replace them. Declare the qualifiers in a pure-Kotlin module so the domain can use them.
- **Context:** use only `@ApplicationContext` in long-lived objects. Never inject an Activity context.

## Error model
- The domain defines a sealed `AppError` (`Network`, `Unauthorized`, `NotFound`, `Server(code)`, `Unknown(cause)`) and `AppResult<T>` (`Success` / `Failure`).
- The data layer catches specific exceptions at its boundary and returns `AppResult`. No raw exceptions travel above the data layer. `CancellationException` is never caught or swallowed.
- Presentation maps `AppError` to a `@StringRes` in one function. It shows the result in `UiState.Error`, or as a snackbar event when cached content stays on screen.

## Threading
- Every `suspend` function is main-safe. A class that does blocking work switches dispatcher itself with `withContext(ioDispatcher)`. Room and Retrofit `suspend`/`Flow` APIs are already main-safe.
- ViewModels expose flows with `stateIn(viewModelScope, WhileSubscribed(5_000), initial)`.
- **Scopes:**
  - `viewModelScope` in ViewModels;
  - `repeatOnLifecycle` or `collectAsStateWithLifecycle` in the UI;
  - WorkManager for work that must outlive the screen.

  Never `GlobalScope`.
