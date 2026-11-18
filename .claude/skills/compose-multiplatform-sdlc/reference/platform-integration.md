# Platform integration reference

How platform-specific code attaches to the shared code, how the iOS app hosts it, and where Android and iOS behave differently. Code shapes are in [code-patterns.md](code-patterns.md#platform-code).

## Where code lives
Share by default. Use the first row that fits:

| Need | Use | Example |
|---|---|---|
| Pure logic, UI, state | `commonMain` | UseCases, ViewModels, screens |
| A platform service with behaviour | An interface in `commonMain`; an implementation in `androidMain` and `iosMain`; bound in each `platformModule` | `SecureStore`, `SyncScheduler`, `AuthClient` |
| A value or a factory | An `expect fun` / `expect val` with an `actual` per platform, or a binding in `platformModule` | The Ktor engine, the database builder, the DataStore path |
| A native view inside a Compose screen | An `expect` Composable whose `actual`s wrap `AndroidView` and `UIKitView` / `UIKitViewController` | A map, a camera preview, a web view |
| An SDK that only has a Swift API | An interface in `commonMain`, implemented in Swift in `iosApp` and passed in at start-up | Firebase Analytics on iOS, a payment SDK |
| A whole screen that must be native | An ADR, a row in the platform matrix, and a navigation hand-off | A Live Activity, a widget, an App Clip |

Each row other than the first is listed in the architecture document's **platform matrix**: the capability, the Android and iOS implementations, why it can't be shared, and its tests.

## expect / actual rules
- **Prefer interfaces + DI.** They can be faked in `commonTest`, which `expect` declarations can't.
- **`expect fun` and `expect val`** are for small factories and values. Keep each `actual` a few lines long.
- **No `expect class`** for services. Expect/actual classes are still Beta, and an interface does the same job.
- **No business logic in an `actual`.** If two `actual`s contain the same `if`, that logic belongs in common code.
- **Name the files** `<Name>.android.kt` and `<Name>.ios.kt`, next to `<Name>.kt` in `commonMain`.

## Platform services
| Capability | Android | iOS | Common API |
|---|---|---|---|
| Secure storage | Keystore-wrapped Tink AEAD, ciphertext in DataStore | Keychain, `kSecAttrAccessible…ThisDeviceOnly` | `SecureStore` |
| Background sync | WorkManager: unique work, constraints, backoff | `BGTaskScheduler` (`BGAppRefreshTask`), plus a sync whenever the app comes to the foreground | `SyncScheduler` |
| Push | Firebase Cloud Messaging | APNs (directly or through FCM) | `PushTokenRegistrar`; payloads parsed in common code |
| Deep links | Verified App Links (`autoVerify`) | Universal Links (Associated Domains + `apple-app-site-association`) | The URL is handed to one common router that validates it |
| Runtime permissions | Runtime permission with a rationale; "don't ask again" | `NS…UsageDescription` in `Info.plist`; the system asks only once, after that only Settings can change it | `PermissionController` |
| Sign-in | Credential Manager; OAuth in Custom Tabs | AuthenticationServices: Sign in with Apple, passkeys, `ASWebAuthenticationSession` | `AuthClient` |
| Biometrics | `BiometricPrompt` with a Keystore-bound `CryptoObject` | Keychain item with a `SecAccessControl` biometry flag | `BiometricAuthenticator` |
| App integrity | Play Integrity | App Attest | `IntegrityTokenProvider`; verified on the server |
| Forced update | Play In-App Updates | Blocking screen with a link to the App Store page | `UpdateChecker` |
| In-app review | Play In-App Review | `AppStore.requestReview` / `SKStoreReviewController` | `ReviewPrompter` |
| Share, photo picking | Share sheet intent; photo picker | `UIActivityViewController`; `PHPickerViewController` | `ShareService`, `PhotoPicker` |
| Analytics, crash reporting | Android SDKs | iOS SDKs (often Swift-only); CrashKiOS or Sentry KMP for Kotlin crashes | `AnalyticsTracker`, `CrashReporter` |

A maintained KMP library may replace a hand-written pair of implementations (e.g. for permissions or settings). Choose it in an ADR, after checking its maintenance and how much of its API it exposes.

## The iOS app
- **Shape.** `iosApp/` is a normal Xcode project. Its Swift code is small:
  - the `@main` App, which starts Koin and hosts `MainViewController()` through a `UIViewControllerRepresentable`;
  - Swift implementations of Kotlin interfaces for iOS-only SDKs;
  - `AppDelegate` hooks only where an SDK needs them (push registration, URL handling).
- **Framework embedding.** A Run Script build phase, before "Compile Sources", runs `./gradlew :shared:embedAndSignAppleFrameworkForXcode`. Xcode's `ENABLE_USER_SCRIPT_SANDBOXING` must be off for that script.
- **Project files that matter for review and release:** `Info.plist` (usage descriptions, `CFBundleLocalizations`, URL types), the entitlements (Associated Domains, push, Keychain groups, Sign in with Apple), `PrivacyInfo.xcprivacy`, the asset catalog (icon, launch screen) and the `.xcconfig` files per configuration.
- **Signing.** Automatic signing for local debug builds. CI uses a distribution certificate and provisioning profiles from CI secrets (e.g. fastlane match, or an App Store Connect API key). Certificates and profiles expire; their renewal dates are in the runbook.

## Swift interop
- **Keep the Swift surface small.** Swift calls a handful of entry points (`MainViewController`, the Koin start-up) and implements a few interfaces. Everything else is `internal`.
- **Objective-C export rules to know:**
  - a top-level function in `Foo.kt` becomes `FooKt.function()` in Swift; a name starting with `init` gets a `do` prefix (`initKoin` → `doInitKoin`);
  - default arguments are not visible to Swift: give Swift-facing functions explicit parameters;
  - generics on interfaces are lost; sealed classes become class hierarchies, not Swift enums;
  - `suspend` functions become completion handlers, and `Flow` has no Swift-native form.
- **Annotations:** `@ObjCName` for a better Swift name; `@HiddenFromObjC` for a public declaration Swift must not see; `@Throws` on any function Swift calls that can throw, otherwise the exception crashes the app.
- **SKIE** (by ADR) turns `Flow` into `AsyncSequence`, `suspend` into `async`, and sealed hierarchies into Swift enums, for teams that write real Swift UI against shared ViewModels.

### Swift implementations of Kotlin interfaces
For an SDK with no Kotlin binding, Kotlin declares the interface and Swift implements it:
1. Declare the interface in `commonMain`, using only types that cross to Swift cleanly (`String`, numbers, `Boolean`, `List`, `Map`, simple data classes).
2. Implement it in Swift in `iosApp`, using the native SDK.
3. Pass the instance to the iOS Koin start-up function, which binds it as a `single`.
4. Implement it for Android in `androidMain` with the Android SDK.

See [code-patterns.md](code-patterns.md#swift-implementation-of-a-kotlin-interface).

## Native views in Compose
- **Wrap them once** in an `expect` Composable (`MapView(state, modifier)`) with `actual`s using `AndroidView` and `UIKitView` / `UIKitViewController`.
- **Keep them few.** Interop views cost performance, and have their own touch, focus, accessibility and z-ordering behaviour. Test each one on real devices of both platforms.
- **State stays in common code.** The native view only renders state and reports events through lambdas.

## Lifecycle differences
| Topic | Android | iOS | Design rule |
|---|---|---|---|
| Configuration changes | Rotation, resizing, locale or theme change recreate the Activity | No recreation | ViewModels hold state; it survives both |
| Process termination | Process death in the background; saved state (`SavedStateHandle`, `rememberSaveable`) is restored | The app is terminated without state restoration; saved state is lost | Anything the user must not lose (drafts, a half-filled form) is written to local storage, not only to saved state |
| Backgrounding | Work continues for a while; WorkManager runs deferred work reliably | The app is suspended within seconds; finishing a write needs `beginBackgroundTask`, and background tasks run when iOS decides | The UI shows "pending" for unsynced changes; sync also runs on foreground |
| Back navigation | System back button and gesture; predictive back | No system back button; edge-swipe back is a gesture only | Every non-root screen shows a back or close control in its top bar |
| Memory pressure | `onTrimMemory`; LMK kills background apps | Memory warnings; jetsam kills the app, even in the foreground | Bound image caches; release big buffers; test on the lowest-RAM devices |
| Permissions | Can be asked again until "don't ask again" | Asked once; later only Settings can change it | Explain before asking; always offer a path when denied |

## Platform look and feel
Compose Multiplatform renders the same Material 3 UI on both platforms. In Phase 2, record in an ADR which components adapt to iOS conventions. Typical choices:
- **Adapt:** the back affordance in the top bar, scroll physics (already native-like), haptics, the share sheet, date and time pickers, alerts for destructive confirmations, text selection and the context menu.
- **Keep Material 3:** layout, typography, colours, buttons, lists and navigation structure, so one design system serves both apps.
- Never adapt by `if (platform == iOS)` scattered in screens. Put the difference behind a design-system component or an `expect` Composable.
