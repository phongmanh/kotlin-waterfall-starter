# Security & privacy reference

Organised by OWASP MASVS category.
- **L1** applies to every app.
- Items marked **(L2)** apply when the app handles sensitive data (finance, health, identity).
- **(R)** items apply when tampering is a real risk.

Choose the level in Phase 1 and verify it in Phase 5.

## The ground rule for secrets
- **Assume the APK will be decompiled.** Anything in it can be extracted.
- **Valuable keys stay on the backend.** API keys for paid or privileged services never ship in the app; it uses short-lived user tokens.
- **Build-time config** (base URLs, public keys) comes from `local.properties` or CI variables into `BuildConfig`, never from Git.

## MASVS-STORAGE
- **Tokens and other sensitive values.** Encrypt them with a key from the **Android Keystore** (e.g. a Tink AEAD with a Keystore-wrapped keyset), and store the result in DataStore.
  - `EncryptedSharedPreferences` (the `security-crypto` library) is deprecated. Don't add it to new code.
- **Where sensitive data must never go:** plain `SharedPreferences` or DataStore, logs, caches, external storage, the clipboard.
- **Backups.** `android:dataExtractionRules` (API 31+) and `android:fullBackupContent` exclude tokens, keys and sensitive databases.
- **Sensitive screens** use `FLAG_SECURE`, which blocks screenshots and recents thumbnails (L2).
- **Logout** clears the user's data.

## MASVS-CRYPTO
- Use platform or Tink primitives. Never write your own crypto or hard-code keys.
- Keep keys in the Keystore: StrongBox-backed when available (L2), and bound to user authentication for high-value actions.

## MASVS-AUTH
- **Sign-in.**
  - Credential Manager for passkeys, passwords and Sign in with Google.
  - OAuth 2 / OIDC with PKCE through Custom Tabs (e.g. AppAuth). Never use a WebView for sign-in.
- **Tokens.**
  - Short-lived access tokens with refresh-token rotation.
  - An OkHttp `Authenticator` refreshes once, and signs the user out if that fails.
  - The refresh is single-flight: when many calls get `401` at once, one refresh runs and the rest wait for it. A call whose token was already replaced retries with the new token instead of refreshing again.
- **Biometrics:** `BiometricPrompt` with a `CryptoObject` bound to a Keystore key, not just a success callback (L2).
- **Authorization** is enforced on the server. The client only hides UI.

## MASVS-NETWORK
- **HTTPS only.**
  - `network_security_config.xml` sets `cleartextTrafficPermitted="false"`.
  - No custom `TrustManager` or `HostnameVerifier` that accepts everything.
- **User-installed CAs** aren't trusted (the default since API 24). Allow them only under `<debug-overrides>`, so QA can inspect traffic with a proxy on debug builds.
- **Certificate pinning** only when the threat model needs it (L2). Then use a backup pin, an `expiration` date on the pin set, a rotation plan, and a remote switch to turn pinning off, so a server certificate change can't lock every user out.
- **Requests:** set OkHttp timeouts. Keep sensitive data out of URLs, because query strings end up in logs.

## MASVS-PLATFORM
- **Components.** Set `android:exported="false"` on every component except the launcher and intentional entry points, and protect exported ones with permissions. The same goes for `ContentProvider`s: not exported unless designed to be, and protected with path permissions.
- **Untrusted input.** Treat every Intent extra, deep link and push payload as untrusted: validate it, then route it. Use verified **App Links** (`autoVerify`) for web links.
- **Intents.** `PendingIntent.FLAG_IMMUTABLE` unless mutability is required. Use explicit intents for internal components.
- **WebView.**
  - JavaScript off unless needed;
  - `allowFileAccess = false`;
  - an allow-list of origins;
  - no `addJavascriptInterface` with untrusted content.
- **Permissions.**
  - Request the minimum, in context, with a rationale.
  - Handle both "denied" and "don't ask again".
  - Prefer the **photo picker**, coarse location and Credential Manager over broad permissions.

## MASVS-CODE
- **Release builds:** R8 on, not debuggable, Timber's debug tree only in debug, and no `Log` calls with user data.
- **Validate all input from outside the app:** server responses, intents, files. Parse JSON into strict types, while tolerating unknown fields.
- **Dependencies.** Scan them in CI and update vulnerable libraries promptly. Vet each third-party SDK: its permissions, the data it collects, its maintenance.
- **Retire insecure versions** by enforcing a minimum supported app version.

## MASVS-RESILIENCE (R)
- **Play Integrity API.** Request a verdict for sensitive actions, and **verify it on the server**.
  - Standard requests (prepared once, then fast) suit frequent checks; classic requests suit rare, high-value actions.
  - Some real users fail the checks. Step up or limit the risky action, rather than blocking the whole app.
- **Root and tamper detection,** and obfuscation beyond R8, only when the threat model justifies them. They never replace server-side checks.

## Privacy
Covers MASVS-PRIVACY.
- **Minimise.** Collect the least data needed, process it on the device when possible, and set a retention period for each data type.
- **Consent** comes before analytics or ad SDKs initialise, where the law requires it.
- **No PII** in logs, analytics events or crash reports. Scrub user IDs, emails and free text.
- **Play disclosures.** The **Data safety** form matches the data inventory, including what SDKs collect. Link the privacy policy in the app and in the store listing.
- **Account deletion.** If the app has accounts, users can delete theirs in the app, and through a web link.
- **Transparency.** At the point of collection, say what's collected and why.

## Quick check for reviewers
- Secrets in code?
- Exported components?
- Cleartext traffic?
- Tokens outside Keystore-backed storage?
- PII in logs?
- A new permission without a rationale?
- A new SDK without a privacy review?
