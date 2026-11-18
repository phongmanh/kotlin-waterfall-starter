# Architecture reference

Clean Architecture + MVVM with unidirectional data flow, written once in `commonMain` and run on Android and iOS. The canonical code for each piece is in [code-patterns.md](code-patterns.md). How platform code is attached is in [platform-integration.md](platform-integration.md).

## Layers
```
presentation (Compose UI, ViewModel) ──▶ domain (UseCases, models, repository interfaces) ◀── data (RepositoryImpl, Ktor, Room, DataStore)
        commonMain                               commonMain                                   commonMain + androidMain/iosMain for drivers and platform services
```
- **Domain is pure common Kotlin.** No `android.*`, `platform.*` (iOS), `java.*`, Compose, Ktor or Room types. It owns the models, the repository interfaces and the error model. `kotlinx.coroutines`, `kotlin.time` and `kotlinx-datetime` are allowed. No DI annotations: dependencies are plain constructor parameters, wired by Koin.
- **Data implements the domain's repository interfaces.** DTOs and entities never leave the data layer; they are mapped with `toDomain()`. Platform pieces (the Ktor engine, the database file path, secure storage) are injected from `androidMain`/`iosMain`.
- **Presentation depends on the domain only.**
  - A ViewModel calls UseCases, never repositories. ViewModels live in `commonMain`.
  - Composables render state and forward events. They hold no business logic.
- **Data flows one way.** State goes down as `StateFlow<UiState>`; events come up through `onAction`. Each screen has exactly one immutable `UiState`.
- **Dependencies point inward.** Koin binds the implementations to the interfaces; platform modules bind the platform implementations.

## Source sets
| Source set | Holds | Rule |
|---|---|---|
| `commonMain` | Domain, data, ViewModels, Compose UI, navigation, DI modules, `composeResources/` | The default home of all code |
| `androidMain` | Android implementations of common interfaces, the Android DI module, `AndroidView` interop | Thin: no business logic, no screens |
| `iosMain` | iOS implementations of common interfaces, the iOS DI module, `MainViewController`, `UIKitView` interop | Thin: no business logic, no screens |
| `commonTest` | Unit, integration and Compose UI tests of common code | Runs on the JVM and on the iOS simulator |
| `androidHostTest` / `androidDeviceTest` | Tests of `androidMain` code (JVM / device) | Only for Android-specific code |
| `iosTest` | Tests of `iosMain` code | Only for iOS-specific code |

- `iosMain` is shared by the `iosArm64` (devices) and `iosSimulatorArm64` targets through the default hierarchy template.
- **Watch the platform share.** When `androidMain` or `iosMain` grows beyond implementations of small interfaces, it's a design smell to raise in review.

## Module layout
Choose one layout in a Phase 2 ADR. Since AGP 9, the Android application must be a module of its own; shared modules use the `com.android.kotlin.multiplatform.library` plugin.

**A. One shared module**, for small apps:
```
androidApp/  # Android application: MainActivity, Application (starts Koin), manifest, icon, signing
iosApp/      # Xcode project: @main App, ContentView hosting MainViewController, Info.plist,
             # entitlements, PrivacyInfo.xcprivacy, assets, Swift implementations of platform services
shared/      # KMP library: commonMain/{domain, data, ui, di}/<feature>/, composeResources/,
             # androidMain/, iosMain/ (MainViewController, platform services), tests
build-logic/ # convention plugins
```

**B. Feature + core modules**, for growing apps (all KMP libraries):
```
androidApp/  iosApp/  build-logic/
shared/                 # umbrella: depends on every module the app needs; the iOS framework is built from it;
                        # holds App(), the root NavHost and the Koin start-up
feature/<name>/         # screens, ViewModels, feature-only UseCases
core/model/             # domain models, AppError, AppDispatchers (pure Kotlin)
core/domain/            # shared UseCases, repository interfaces (pure Kotlin)
core/data/              # RepositoryImpl, mappers, DI bindings
core/network/  core/database/  core/datastore/  core/platform/   # platform services (SecureStore, SyncScheduler…)
core/designsystem/      # theme, tokens, base components
core/ui/                # shared screen-level components and helpers
core/testing/           # fakes, test-data builders
```
- In layout B, features never depend on other features. They connect through navigation routes and core modules.
- **One framework for iOS.** Xcode links a single Kotlin framework built from the umbrella `shared` module. Several frameworks would each carry their own copy of the Kotlin runtime, and their types would not be interchangeable in Swift.

**Size rule.** Choose B if any of these hold; otherwise choose A:
- more than ~5 features are planned;
- more than ~3 developers, or 2+ teams;
- build times already hurt (Kotlin/Native linking is the usual bottleneck);
- code will be shared with another app.

In either layout, **package by feature inside each layer** (`…/notes/`, `…/settings/`). That keeps a later move from A to B mechanical.

## Default stack
Always use the latest stable versions, declared in `gradle/libs.versions.toml`. A deviation needs an ADR.

| Concern | Default | Notes |
|---|---|---|
| Language | Kotlin (K2) | Swift only in `iosApp`: the entry point and glue for iOS-only SDKs |
| Build | Gradle Kotlin DSL, version catalog, convention plugins in `build-logic` | Android app in its own module (AGP 9); shared modules on `com.android.kotlin.multiplatform.library` |
| Targets | Android, `iosArm64`, `iosSimulatorArm64` | `iosX64` only while someone still builds on an Intel Mac; desktop and web only by ADR |
| iOS integration | A static framework (`isStatic = true`) built from the umbrella module, embedded by the `embedAndSignAppleFrameworkForXcode` build phase | Swift Package Manager or CocoaPods distribution by ADR |
| UI | Compose Multiplatform + Material 3, shared in `commonMain` | A native SwiftUI/UIKit screen only by ADR, listed in the platform matrix |
| Resources | Compose Multiplatform resources (`composeResources/`, generated `Res`) | No Android `R` in shared code |
| Navigation | Navigation Compose (JetBrains multiplatform artifact) with type-safe `@Serializable` routes | Navigation 3 (multiplatform since Compose Multiplatform 1.10) by ADR |
| ViewModel and lifecycle | The multiplatform `androidx.lifecycle` ViewModel and lifecycle-compose artifacts | `collectAsStateWithLifecycle` works in common code |
| DI | Koin (`koin-core`, `koin-compose`, `koin-compose-viewmodel`) | Compile-time DI (e.g. Metro, kotlin-inject) by ADR. Hilt is Android-only |
| Async | Coroutines + Flow | No `GlobalScope`; no RxJava |
| Network | Ktor client + kotlinx.serialization; OkHttp engine on Android, Darwin engine on iOS | Not Retrofit |
| Database | Room (KMP) with the bundled SQLite driver; schemas exported and committed | Room 3 (`androidx.room3`) for new projects; Room 2.7+ (`androidx.room`) in existing ones. SQLDelight by ADR |
| Key-value storage | DataStore Preferences (KMP) | Not `SharedPreferences` or `NSUserDefaults` directly |
| Secure storage | A `SecureStore` interface: Android Keystore + Tink; iOS Keychain | See [security-privacy.md](security-privacy.md#masvs-storage) |
| Time | `Instant` and `Clock` from `kotlin.time`; kotlinx-datetime for time zones and calendar dates | Never `java.time` or `System.currentTimeMillis()` in shared code |
| Background work | A `SyncScheduler` interface: WorkManager on Android; `BGTaskScheduler` plus sync-on-foreground on iOS | iOS decides when, or whether, background work runs |
| Images | Coil 3 (multiplatform) with its Ktor network fetcher | |
| Paging | Paging 3 (multiplatform `paging-common` and `paging-compose`) | For lists that can grow |
| Logging | Kermit | Debug logging in debug builds only |
| Crash and performance | Firebase Crashlytics with CrashKiOS for readable Kotlin crashes on iOS, or the Sentry KMP SDK, chosen by ADR | R8 mapping files and dSYMs uploaded by CI |
| Sign-in | Android Credential Manager; iOS AuthenticationServices (Sign in with Apple, passkeys, `ASWebAuthenticationSession`); OAuth 2 + PKCE in the system browser on both | Behind a common `AuthClient` interface |
| App integrity | Play Integrity (Android), App Attest (iOS) | Verdicts checked on the server |
| Updates | Play In-App Updates (Android); a minimum-version check that links to the App Store (iOS) | For forced updates |
| Swift interop | Plain Objective-C export for the small Swift surface; SKIE when Swift must consume Flows, suspend functions or sealed types | Swift export by ADR |
| Static analysis | ktlint, detekt (all source sets), Android Lint (Android modules), SwiftLint (`iosApp`) | |
| Testing | kotlin-test, kotlinx-coroutines-test, Turbine, fakes, Ktor `MockEngine`, Compose Multiplatform UI tests (`runComposeUiTest`), Roborazzi; XCTest/XCUITest for iOS-only code and smoke tests | MockK is JVM-only: use fakes, and Mokkery where a mock is unavoidable. See [testing.md](testing.md) |
| Performance tools | Android: Baseline Profiles, Macrobenchmark, LeakCanary (debug). iOS: Xcode Instruments, MetricKit, Xcode Organizer | |
| Coverage | Kover | Measures the JVM run of common code |

## Gradle conventions
- **One place for shared config.** Targets, the framework settings (`baseName`, `isStatic`), `compileSdk`, `minSdk`, the JVM toolchain and Compose options live only in convention plugins.
- **Android release builds** (`androidApp`) set `isMinifyEnabled = true` and `isShrinkResources = true`. Keep R8 keep-rules next to the code that needs them (e.g. serialization, Room).
- **iOS release builds** come from Xcode's Release configuration, which `embedAndSignAppleFrameworkForXcode` passes to Gradle, so the Kotlin framework is built in release mode too.
- **Config per environment** is a common `AppConfig` data class (base URL, flag defaults), built by each entry point from its platform's build config and passed to Koin at start-up:
  - Android: `BuildConfig` fields per build type;
  - iOS: `Info.plist` values filled from `.xcconfig` files per Xcode configuration.

  Secrets come from `local.properties`, untracked `.xcconfig` files or CI variables, never from Git. Anything in the APK or the IPA is public, so real secrets stay on the server.
- **Build speed:** build cache, configuration cache, Kotlin/Native caches (keep `~/.konan` cached in CI). Locally, link only the simulator architecture you run.
- **Dependency scope:** `api` only when a type is part of the module's public API; otherwise `implementation`. The umbrella module `export`s only the modules Swift needs.
- **Visibility:** mark everything `internal` unless another module uses it. Every public declaration in the umbrella framework ends up in the Objective-C header Swift sees, which costs build time and binary size.

## Dependency injection (Koin)
- **Modules:** one per feature or layer (`notesModule`, `networkModule`), plus one `platformModule` per platform (`expect val platformModule: Module` with an `actual` in `androidMain` and `iosMain`).
- **Definitions:**
  - `single` for the `HttpClient`, the database and DAOs, DataStore, repositories and platform services;
  - `factoryOf` for UseCases;
  - `viewModelOf` for ViewModels, retrieved in Compose with `koinViewModel()`.
- **Bind interfaces:** `singleOf(::NoteRepositoryImpl) bind NoteRepository::class`.
- **Dispatchers** are injected as an `AppDispatchers(io, default)` data class declared in a pure-Kotlin module, so tests can replace them.
- **Start Koin once:** in `Application.onCreate` on Android (with `androidContext`), and from the Swift `App` initialiser on iOS, before the first `MainViewController` is created.
- **Context:** only the application context in long-lived objects (`androidContext()`). Never hold an Activity or a `UIViewController` in a singleton.
- **Check the graph in a test.** Koin resolves at runtime, so a JVM test starts the full graph with test bindings for the platform module and resolves every ViewModel and UseCase ([testing.md](testing.md#snippets)). A missing binding then fails CI, not the app.

## Error model
- The domain defines a sealed `AppError` (`Network`, `Unauthorized`, `NotFound`, `Server(code)`, `Unknown(cause)`) and `AppResult<T>` (`Success` / `Failure`).
- The data layer catches specific exceptions at its boundary and returns `AppResult`. No raw exceptions travel above the data layer. `CancellationException` is never caught or swallowed.
  - Ktor with `expectSuccess = true` throws `ResponseException` for non-2xx responses.
  - Connectivity failures and timeouts are `kotlinx.io.IOException` on both the OkHttp and Darwin engines.
- Presentation maps `AppError` to a `StringResource` (`Res.string.…`) in one function. It shows the result in `UiState.Error`, or as a snackbar event when cached content stays on screen.
- **Uncaught exceptions on iOS** terminate the app like a native crash. Never let one escape a coroutine or a Swift call; the crash reporter's Kotlin integration makes the ones that do readable.

## Threading
- Every `suspend` function is main-safe. A class that does blocking work switches dispatcher itself with `withContext(dispatchers.io)`. Ktor and Room `suspend`/`Flow` APIs are already main-safe.
- `Dispatchers.IO` exists on iOS too (import `kotlinx.coroutines.IO` in common code), but it's still injected, never hard-coded.
- ViewModels expose flows with `stateIn(viewModelScope, WhileSubscribed(5_000), initial)`.
- **Scopes:**
  - `viewModelScope` in ViewModels;
  - `collectAsStateWithLifecycle` and lifecycle-aware collection in the UI (the iOS `ComposeUIViewController` provides a lifecycle);
  - the `SyncScheduler` for work that must outlive the screen.

  Never `GlobalScope`.
- **Swift callers.** Kotlin `suspend` functions called from Swift complete on the main thread. Don't expose them to Swift without SKIE, and keep heavy work inside Kotlin.

## Migrating an Android app to KMP
Bring an Android app to iOS one layer at a time. **Each step ships on Android alone** before the next starts, so the app is never in a half-migrated state at release time.

| Step | Move to `commonMain` | Replace |
|---|---|---|
| 0 | Project structure | Split the Android app module out (`androidApp`); add the shared KMP module and the iOS targets; an empty iOS app that launches |
| 1 | Domain models, repository interfaces, UseCases | `java.time` → `kotlin.time`; `javax.inject` annotations → plain constructors |
| 2 | Data layer | Retrofit → Ktor; Room → Room KMP (bundled driver); `SharedPreferences` → DataStore; Hilt → Koin (or keep Hilt only in `androidApp` until step 3, never both in shared code) |
| 3 | ViewModels | `@HiltViewModel` → `viewModelOf`; `@StringRes` → `StringResource` |
| 4 | Compose UI | Jetpack Compose → Compose Multiplatform (mostly imports); `R` → `Res`; Android-only APIs behind interfaces or `expect` functions |
| 5 | iOS app | `MainViewController`, Swift entry point, platform services, iOS signing and release |

- Before step 1, list every Android-only dependency and its replacement in an ADR. An SDK with no KMP or iOS equivalent becomes an interface with a Swift implementation ([platform-integration.md](platform-integration.md#swift-implementations-of-kotlin-interfaces)).
- Keep the Room schema version and migrations across the move: the upgrade test from the last Android-only release is mandatory.
