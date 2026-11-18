# Release checklist: <App> <version> (Android <versionCode> · iOS <build number>)

| Release owner | Target date | Release plan | G5 decision |
|---|---|---|---|
| <name> | YYYY-MM-DD | Android: internal → closed → production (staged). iOS: TestFlight → App Review → phased release | <date, approver, per platform> |

## Build
- [ ] Both builds made by CI from the tag `v<version>`
- [ ] Same version name on both platforms; `versionCode` and `CFBundleVersion` higher than every published build
- [ ] Android: release build type with R8 and resource shrinking on; not debuggable; debug tools excluded
- [ ] Android: signed with the upload key from CI secrets; Play App Signing enabled; Baseline Profile included
- [ ] Android: mapping file archived, and uploaded to Play Console and the crash reporter
- [ ] iOS: Release configuration; signed with the distribution certificate and profile from CI secrets
- [ ] iOS: dSYMs (including the Kotlin framework's) archived and uploaded to the crash reporter
- [ ] iOS: built with the Xcode and SDK versions Apple currently requires; privacy manifest included

## Google Play Console
- [ ] Target API level meets Play's current requirement
- [ ] Data safety form matches the data inventory, including SDKs
- [ ] Sensitive permissions declared and justified
- [ ] Content rating and privacy policy URL set; account-deletion link if the app has accounts
- [ ] Store listing, phone and tablet screenshots, and release notes for each locale

## App Store Connect
- [ ] App Privacy details match the data inventory, including SDKs; ATT prompt present if the app tracks
- [ ] Export-compliance (encryption) answers given
- [ ] Age rating and privacy policy URL set; in-app account deletion if the app has accounts
- [ ] Screenshots for the required iPhone (and iPad) sizes, and release notes for each locale
- [ ] Review notes and a working demo account for App Review
- [ ] Release mode chosen: manual after approval, or automatic; phased release on

## Readiness
- [ ] G5 go decision recorded for each platform; test summary report approved
- [ ] Feature flags set; kill switches tested on both platforms; minimum-version config ready for both
- [ ] Dashboards and alerts live for both platforms; on-call owner named
- [ ] Signing material valid beyond the hypercare period
- [ ] Support team briefed; known issues documented per platform

## Rollout
| Step | Platform | Track / % | Earliest date | Halt if… | Decision |
|---|---|---|---|---|---|
| 1 | Android | Internal | | Any S1 defect | |
| 2 | iOS | TestFlight internal | | Any S1 defect | |
| 3 | Android | Closed testing | | Crash rate > <n>% | |
| 4 | iOS | TestFlight external, then App Review | | Crash-free sessions < <n>% | |
| 5 | Android | Production 1% → 5% → 20% → 50% → 100% (≥ 24 h per step) | | Crash rate > <n>%, ANR rate > <n>%, KPI drop > <n>% | |
| 6 | iOS | Phased release over 7 days | | Crash-free sessions < <n>%, hang rate > <n>, KPI drop > <n>% | |

On a halt:
1. Halt the staged rollout in Play Console; pause the phased release in App Store Connect.
2. Disable the feature flag or kill switch (both platforms).
3. Fix forward with a new build number; ask for an expedited App Review if the fix is critical.

## Hypercare (<n> days)
- [ ] Daily check of Android vitals, iOS crash and hang reports, reviews in both stores and support tickets; findings logged

## Handover and sign-off
- [ ] Runbook (both platforms, signing and expiry dates), dashboards, open defects and known limitations handed over to <maintenance owner>
- [ ] RTM closed; lessons learned recorded

| Role | Name | Decision | Date |
|---|---|---|---|
