# Phase 6: Release
**Gate:** G6 Launch accepted
**Deliverables:** completed [release checklist](../templates/release-checklist.md), rollout record for each store, handover pack
**Load:** [performance-reliability](../reference/performance-reliability.md#observability), [security-privacy](../reference/security-privacy.md#privacy)

## Goal
Ship the approved builds to Google Play and the App Store safely and in stages, watch them in production, and hand them over to the team that runs them.

## Entry criteria
- G5 approved, with the go decision recorded for each platform.
- Play Console and App Store Connect access is in place; the store-listing owner and the on-call owner are named.

## Activities
1. **Build and signing.**
   - CI builds both releases from the same tagged commit.
   - Versions: one version name for both apps (`versionName` = `CFBundleShortVersionString`); `versionCode` and `CFBundleVersion` only go up.
   - Android: the upload key lives in CI secrets; Play App Signing holds the app signing key. Archive the R8 mapping file and upload it to Play Console and the crash reporter.
   - iOS: the distribution certificate and provisioning profile live in CI secrets. Archive the dSYMs, including the Kotlin framework's, and upload them to the crash reporter.
2. **Store set-up.**
   - **Play Console:**
     - the Data safety form matches the data inventory, including what SDKs collect;
     - sensitive permissions (e.g. background location) are declared and justified;
     - the target API level meets Play's current requirement;
     - content rating, the privacy policy URL, and an account-deletion link if the app has accounts;
     - store listing, phone and tablet screenshots, and release notes for each locale.
   - **App Store Connect:**
     - App Privacy details match the data inventory, and the privacy manifest is in the build (including SDKs' manifests);
     - the build was made with the Xcode and iOS SDK versions Apple currently requires;
     - export-compliance (encryption) answers;
     - age rating, the privacy policy URL, in-app account deletion if the app has accounts;
     - screenshots for the required iPhone and iPad sizes, and release notes for each locale;
     - review notes and a demo account for App Review.
3. **Rollout through stages.**
   - **Android:** internal → closed testing → production with a **staged rollout**, e.g. 1% → 5% → 20% → 50% → 100%, with at least 24 hours per step.
   - **iOS:** TestFlight internal → TestFlight external (needs a beta review) → App Review → release with **phased release**, which spreads automatic updates over 7 days. Anyone can still update manually from the App Store, and new installs get the new version right away.
   - Plan for App Review time, including a possible rejection, before any announced date. Release manually after approval if both apps must launch together.
4. **Halt criteria**, agreed before the rollout starts, per platform. For example:
   - the crash, ANR or hang rate goes above its target;
   - a new S1 defect appears;
   - a key KPI drops by more than an agreed percentage.

   On a halt:
   1. Halt the staged rollout in Play Console, or pause the phased release in App Store Connect.
   2. Switch off the feature flag or kill switch. It covers both platforms at once.
   3. Ship a fix forward. Neither store can roll a release back. On iOS, ask for an expedited review for a critical fix.
5. **Safety nets.**
   - Remote config for the feature flags and kill switches, shared by both apps.
   - A minimum-supported-version check: In-App Updates on Android, a blocking screen with an App Store link on iOS.
6. **Hypercare** (e.g. 1–2 weeks).
   - Review Android vitals, the iOS crash and hang reports (crash reporter, Xcode Organizer), reviews in both stores and support tickets every day.
   - Name the on-call owner.
7. **Handover** to the maintenance team:
   - a runbook covering both builds and releases, signing (including the Apple certificate and profile expiry dates), disabling a feature through flags, and hotfixes on each store;
   - dashboards and alert owners per platform;
   - open defects and known limitations per platform.
8. **Close.**
   - Finish the RTM (requirement → release, per platform).
   - Record lessons learned.
   - Archive the baselines.

## Exit checklist (G6)
- [ ] Android rollout and iOS phased release reached 100% with no halt criteria hit, or every halt resolved
- [ ] Stability and KPIs within target on both platforms during hypercare
- [ ] Mapping files and dSYMs uploaded; dashboards and alerts live for both platforms
- [ ] Handover accepted by the maintenance owner
- [ ] RTM closed; lessons learned recorded

## Pitfalls
- **Releasing to 100% at once,** or forgetting that iOS phased release doesn't hold back manual updates and new installs.
- **Announcing a date before App Review has approved the build.**
- **Inventing halt criteria** after things have gone wrong.
- **Losing signing material:** the Android upload key on a laptop, or an expired Apple distribution certificate on release day.
- **Missing dSYMs** for the Kotlin framework, so iOS crashes can't be read.
- **Store disclosures that don't match** what an SDK actually collects, leading to a rejection or a policy strike.
- **No kill switch** for a risky feature.
