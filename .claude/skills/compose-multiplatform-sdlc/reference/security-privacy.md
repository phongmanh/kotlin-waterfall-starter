# Security & privacy reference

Organised by OWASP MASVS category, for Android and iOS. The shared code makes most controls common; storage, platform and store disclosures differ per platform.
- **L1** applies to every app.
- Items marked **(L2)** apply when the app handles sensitive data (finance, health, identity).
- **(R)** items apply when tampering is a real risk.

Choose the level in Phase 1 and verify it on both platforms in Phase 5.

## The ground rule for secrets
- **Assume both the APK and the IPA will be reverse-engineered.** Strings in a Kotlin/Native binary are as easy to extract as strings in a DEX file.
- **Valuable keys stay on the backend.** API keys for paid or privileged services never ship in the app; it uses short-lived user tokens.
- **Build-time config** (base URLs, public keys) comes from `local.properties`, untracked `.xcconfig` files or CI variables, through `AppConfig`. Never from Git.

## MASVS-STORAGE
- **Tokens and other sensitive values** go through the common `SecureStore` interface:
  - **Android:** encrypt with a key from the **Android Keystore** (e.g. a Tink AEAD with a Keystore-wrapped keyset), and store the result in DataStore. `EncryptedSharedPreferences` (`security-crypto`) is deprecated; don't add it.
  - **iOS:** store in the **Keychain** with an accessibility of `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly`, or `…WhenUnlockedThisDeviceOnly` for data needed only in the foreground. `ThisDeviceOnly` items are never restored onto another device.
- **Where sensitive data must never go:** plain DataStore, `NSUserDefaults`, logs, caches, the clipboard, files outside the app container.
- **Backups.**
  - Android: `android:dataExtractionRules` (API 31+) and `android:fullBackupContent` exclude tokens, keys and sensitive databases.
  - iOS: files in the app container go to iCloud and device backups by default. Mark sensitive files with `NSURLIsExcludedFromBackupKey`, and keep secrets in `ThisDeviceOnly` Keychain items.
- **Files at rest on iOS.** Sensitive databases and files use a file-protection class that keeps them encrypted while the device is locked, where background access allows it (L2).
- **Sensitive screens (L2).**
  - Android: `FLAG_SECURE` blocks screenshots and the recents thumbnail.
  - iOS: cover the content when the app moves to the background, so the app-switcher snapshot doesn't show it.
- **Logout** clears the user's data on both platforms: database, DataStore, `SecureStore`, image caches.

## MASVS-CRYPTO
- Use platform or Tink primitives (Android) and CryptoKit or the Security framework (iOS). Never write your own crypto or hard-code keys. A multiplatform crypto library needs an ADR.
- Keep keys in hardware where available: StrongBox or the Keystore TEE on Android, the Secure Enclave on iOS (L2). Bind keys to user authentication for high-value actions.

## MASVS-AUTH
- **Sign-in** goes through a common `AuthClient` interface.
  - Android: Credential Manager for passkeys, passwords and Sign in with Google.
  - iOS: AuthenticationServices for passkeys and Sign in with Apple.
  - OAuth 2 / OIDC with PKCE in the system browser: Custom Tabs on Android, `ASWebAuthenticationSession` on iOS. Never use a WebView for sign-in.
  - App Store rule: an app that offers third-party or social sign-in must also offer an equivalent privacy-focused option such as Sign in with Apple. Check the current App Review Guidelines in Phase 1.
- **Tokens.**
  - Short-lived access tokens with refresh-token rotation.
  - Ktor's `Auth` plugin refreshes once and signs the user out if that fails.
- **Biometrics (L2)** unlock a key, not a boolean:
  - Android: `BiometricPrompt` with a `CryptoObject` bound to a Keystore key.
  - iOS: a Keychain item protected by a `SecAccessControl` biometry flag, not just an `LAContext.evaluatePolicy` callback.
- **Authorization** is enforced on the server. The client only hides UI.

## MASVS-NETWORK
- **HTTPS only.**
  - Android: `network_security_config.xml` sets `cleartextTrafficPermitted="false"`.
  - iOS: App Transport Security stays on. No `NSAllowsArbitraryLoads`; any exception domain needs an ADR.
  - No custom trust manager or challenge handler that accepts every certificate.
- **Certificate pinning** only when the threat model needs it (L2), on both Ktor engines (OkHttp's `CertificatePinner`, the Darwin engine's certificate pinner), with a backup pin and a rotation plan.
- **Requests:** set Ktor timeouts. Keep sensitive data out of URLs, because query strings end up in logs.
- **Logging:** Ktor's `Logging` plugin only in debug builds, with the `Authorization` header sanitised.

## MASVS-PLATFORM
- **Android components.** Set `android:exported="false"` on every component except the launcher and intentional entry points; protect exported ones with permissions. `PendingIntent.FLAG_IMMUTABLE` unless mutability is required. Explicit intents for internal components.
- **Untrusted input.** Treat every deep link, push payload and Intent extra as untrusted. Both platforms hand the URL to **one common router** that validates it, then navigates.
  - Android: verified **App Links** (`autoVerify`).
  - iOS: **Universal Links**. Custom URL schemes can be claimed by any app, so they never carry sensitive data or actions.
- **Web views** (`WebView`, `WKWebView`): JavaScript off unless needed; no file access; an allow-list of origins; no JavaScript bridge with untrusted content.
- **Permissions.**
  - Request the minimum, in context, with a rationale.
  - Android: handle "denied" and "don't ask again".
  - iOS: every protected resource needs a clear `NS…UsageDescription` in `Info.plist`. The system asks once; after a denial, only Settings can change it.
  - Prefer options that need no permission: the photo pickers, coarse or approximate location, Credential Manager and AuthenticationServices.
- **Pasteboard and keyboard.** Disable autocorrect and suggestions for secret fields; don't put secrets on the clipboard.

## MASVS-CODE
- **Release builds.**
  - Android: R8 on, not debuggable.
  - iOS: built from the Release configuration; debug symbols stripped from the binary and kept as dSYMs for the crash reporter.
  - Kermit's debug output only in debug builds; no logs with user data.
- **Validate all input from outside the app:** server responses, deep links, files. Parse JSON into strict types, while tolerating unknown fields.
- **Dependencies.** Scan Gradle and iOS (Swift Package Manager or CocoaPods) dependencies in CI, and update vulnerable libraries promptly. Vet each third-party SDK on both platforms: its permissions, the data it collects, its privacy manifest, its maintenance.
- **Retire insecure versions** by enforcing a minimum supported app version on both platforms.

## MASVS-RESILIENCE (R)
- **App integrity.** Play Integrity on Android, App Attest on iOS. Request a verdict for sensitive actions, and **verify it on the server**.
- **Root, jailbreak and tamper detection,** and obfuscation beyond R8, only when the threat model justifies them. They never replace server-side checks.

## Privacy
Covers MASVS-PRIVACY.
- **Minimise.** Collect the least data needed, process it on the device when possible, and set a retention period for each data type.
- **Consent** comes before analytics or ad SDKs initialise, where the law requires it. On iOS, tracking users across other companies' apps or websites requires **App Tracking Transparency** permission.
- **No PII** in logs, analytics events or crash reports. Scrub user IDs, emails and free text.
- **Store disclosures,** all generated from the one data inventory:
  - Google Play **Data safety** form;
  - App Store **App Privacy** details ("nutrition labels");
  - the iOS **privacy manifest** (`PrivacyInfo.xcprivacy`): collected data types, tracking domains, and the reasons for each required-reason API the app or its libraries use (e.g. user defaults, file timestamps). Third-party SDKs bring their own manifests; check them.
  - A privacy policy link in the app and in both store listings.
- **Account deletion.** If the app has accounts, users can start deleting theirs in the app on both platforms, and Google Play also needs a web link.
- **Transparency.** At the point of collection, say what's collected and why.

## Quick check for reviewers
- Secrets in code, `Info.plist` or `.xcconfig` files in Git?
- Exported Android components? Sensitive data in a custom URL scheme?
- Cleartext traffic, or an ATS exception?
- Tokens outside `SecureStore`?
- PII in logs?
- A new permission without a rationale and an iOS usage description?
- A new SDK without a privacy review, a Data safety update and a privacy-manifest check?
