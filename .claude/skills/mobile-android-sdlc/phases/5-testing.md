# Phase 5: Testing
**Gate:** G5 Release readiness (go/no-go). Never skipped or combined.
**Deliverables:** test execution reports, defect log, UAT sign-off, test summary report (in the [test plan](../templates/test-plan.md)), RTM update
**Load:** [testing](../reference/testing.md), [security-privacy](../reference/security-privacy.md), [performance-reliability](../reference/performance-reliability.md), [ui-ux](../reference/ui-ux.md)

## Goal
Prove on real devices that the app meets every requirement and NFR, and give the go/no-go decision a base of evidence.

## Entry criteria
- G4 approved; the RC is installed on the test devices.
- The test plan is approved; environments, accounts and data are ready.

## Activities
1. **Run the test levels** from the master test plan. Unit tests already pass in CI. System, NFR and acceptance tests use the **RC build** (release config, R8 on).

   | Level | What | Tools |
   |---|---|---|
   | Integration (`IT-`) | Repositories with in-memory Room and MockWebServer; DAO and migration tests | JUnit, Room testing, MockWebServer |
   | UI (`UI-`) | Critical flows; screenshots of key screens | Compose UI test; Roborazzi or Compose Preview Screenshot Testing |
   | System (`ST-`) | End to end against staging, on the device matrix | Automated and manual, on a device farm (e.g. Firebase Test Lab) |
   | Acceptance (`AT-`) | The product owner and pilot users, on the Play internal or closed track | The acceptance outline |
2. **NFR tests**, each against its requirement's target:
   - **Performance:**
     - Macrobenchmark cold start and scrolling on the reference low-end device;
     - compare runs with and without the Baseline Profile.
   - **Accessibility:**
     - Accessibility Scanner on every screen;
     - a TalkBack walkthrough of the critical flows;
     - maximum font scale and display size;
     - dark mode.
   - **Security:**
     - the [MASVS checklist](../reference/security-privacy.md);
     - a static scan of the APK (e.g. MobSF);
     - check exported components, backups and logs on a device;
     - try deep links with malicious input.
   - **Reliability:**
     - airplane mode, a throttled network, switching networks;
     - process death ("Don't keep activities", `adb shell am kill`);
     - rotation and window resizing.
   - **Upgrade:**
     - install the previous store version, create data, upgrade to the RC, check the data;
     - run the Room migration tests from every shipped schema version.
   - **Compatibility:** the device matrix, including `minSdk`, the latest Android version, a low-RAM device, a tablet and a foldable.
   - **i18n:** the pseudo-locales `en-XA` (long text) and `ar-XB` (RTL), plus the formats of each supported locale.
3. **Defects.**
   - Log each one with its steps, device, build and severity:
     - S1: crash, data loss or security issue;
     - S2: a Must FR is broken, with no workaround;
     - S3: a workaround exists;
     - S4: cosmetic.
   - Fix them in a new RC. Re-run the affected tests plus a regression subset.
4. **Test summary report.** Results per level, NFR results against their targets, open defects by severity, residual risks, and a recommendation.
5. **Go/no-go.** Present the report and the G5 checklist to the product owner, the tech lead and the QA lead.

## Exit checklist (G5)
- [ ] Every Must FR has a passing `AT-` or `ST-` test; the RTM shows full coverage
- [ ] Every NFR measured and within target, or the gap formally accepted
- [ ] No open S1 or S2 defects; S3 defects reviewed and accepted
- [ ] MASVS checklist passed at the agreed level
- [ ] Upgrade and migration tests passed
- [ ] UAT signed off; test summary report approved
- [ ] Release notes, Data safety answers and store assets ready

## Pitfalls
- **Testing the debug build.** Differences in R8, signing and logging only show up in release.
- **Only flagship devices on fast Wi-Fi.**
- **Skipping the upgrade test,** the only way to catch a broken migration before users do.
- **Lowering the exit criteria** to hit a date, instead of escalating the risk.
