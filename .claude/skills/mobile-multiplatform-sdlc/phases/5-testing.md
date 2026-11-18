# Phase 5: Testing
**Gate:** G5 Release readiness (go/no-go), for both platforms. Never skipped or combined.
**Deliverables:** test execution reports, defect log, UAT sign-off, test summary report (in the [test plan](../templates/test-plan.md)), RTM update
**Load:** [testing](../reference/testing.md), [security-privacy](../reference/security-privacy.md), [performance-reliability](../reference/performance-reliability.md), [ui-ux](../reference/ui-ux.md)

## Goal
Prove on real Android and iOS devices that the app meets every requirement and NFR, and give the go/no-go decision a base of evidence for each platform.

## Entry criteria
- G4 approved; the RCs are installed on the test devices of both platforms.
- The test plan is approved; environments, accounts and data are ready.

## Activities
1. **Run the test levels** from the master test plan. Unit tests already pass in CI on the JVM and the iOS simulator. System, NFR and acceptance tests use the **RC builds**: the release AAB (R8 on) and the Release-configuration iOS build from TestFlight.

   | Level | What | Tools |
   |---|---|---|
   | Integration (`IT-`) | Repositories with `MockEngine`; DAO and migration tests; platform service implementations | kotlin-test, Room testing, `MockEngine`, platform test source sets |
   | UI (`UI-`) | Critical flows on both platforms; screenshots of key screens | Common Compose UI tests; Roborazzi; XCUITest smoke test |
   | System (`ST-`) | End to end against staging, on both device matrices | Automated and manual, on device farms (e.g. Firebase Test Lab, a cloud iOS device farm) |
   | Acceptance (`AT-`) | The product owner and pilot users | The acceptance outline, on the Play internal or closed track and TestFlight |
2. **NFR tests**, each against its requirement's target on each platform:
   - **Performance:**
     - Android: Macrobenchmark cold start and scrolling on the reference low-end device; compare with and without the Baseline Profile.
     - iOS: Instruments (App Launch, hitches, Time Profiler) on the reference iPhone, Release build only.
     - App size from both store reports.
   - **Accessibility:**
     - Android: Accessibility Scanner on every screen; a TalkBack walkthrough of the critical flows.
     - iOS: Xcode's Accessibility Inspector on every screen; a VoiceOver walkthrough of the critical flows.
     - Largest font size, dark mode, reduced motion, on both.
   - **Security:**
     - the [MASVS checklist](../reference/security-privacy.md) on both platforms;
     - a static scan of the APK and the IPA (e.g. MobSF);
     - Android: exported components, backups and logs on a device;
     - iOS: ATS exceptions, Keychain accessibility, files excluded from backup, the device console for leaked data;
     - deep links and Universal Links with malicious input.
   - **Reliability:**
     - airplane mode, a throttled network (Android emulator network profiles; the iOS Network Link Conditioner), switching networks;
     - Android: process death ("Don't keep activities", `adb shell am kill`), rotation and window resizing;
     - iOS: terminate the app in the background and reopen it; background for hours, then foreground (does sync recover?); memory pressure on the lowest-RAM iPhone.
   - **Upgrade:**
     - on each platform, install the previous store version, create data, upgrade to the RC, check the data;
     - run the Room migration tests from every shipped schema version.
   - **Compatibility:** both device matrices, including `minSdk` and the oldest supported iOS, the latest of each, low-RAM devices, Android tablet and foldable, iPad.
   - **i18n:** Android pseudo-locales `en-XA` (long text) and `ar-XB` (RTL); the iOS double-length and right-to-left pseudolanguages; the formats of each supported locale; the language list in iOS Settings.
3. **Store readiness.** Check the iOS build against the current App Review Guidelines (sign-in options, account deletion, payments, permissions wording) and the Android build against Play policies, before submitting.
4. **Defects.**
   - Log each one with its steps, platform, device, build and severity:
     - S1: crash, data loss or security issue;
     - S2: a Must FR is broken, with no workaround;
     - S3: a workaround exists;
     - S4: cosmetic.
   - A defect in shared code is fixed once and re-tested on **both** platforms.
   - Fix them in a new RC. Re-run the affected tests plus a regression subset.
5. **Test summary report.** Results per level and platform, NFR results against their targets, open defects by severity and platform, residual risks, and a recommendation per platform.
6. **Go/no-go.** Present the report and the G5 checklist to the product owner, the tech lead and the QA lead. A go for one platform only is possible, but it's an explicit decision with its own recorded risk.

## Exit checklist (G5)
- [ ] Every Must FR has a passing `AT-` or `ST-` test on each of its platforms; the RTM shows full coverage
- [ ] Every NFR measured on each platform and within target, or the gap formally accepted
- [ ] No open S1 or S2 defects on either platform; S3 defects reviewed and accepted
- [ ] MASVS checklist passed at the agreed level on both platforms
- [ ] Upgrade and migration tests passed on both platforms
- [ ] UAT signed off; test summary report approved
- [ ] Store readiness checked; release notes, Data safety answers, App Privacy details and store assets ready

## Pitfalls
- **Testing debug builds.** R8, signing, logging and Kotlin/Native optimisation only show their effect in release.
- **Testing iOS on the newest iPhone only,** where Compose performance looks fine.
- **Re-testing a shared-code fix on one platform only.**
- **Skipping the upgrade test,** the only way to catch a broken migration before users do.
- **Finding App Review issues at submission,** when the release date is already announced.
- **Lowering the exit criteria** to hit a date, instead of escalating the risk.
