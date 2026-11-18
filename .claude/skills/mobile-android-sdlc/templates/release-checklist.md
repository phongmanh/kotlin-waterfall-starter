# Release checklist: <App> <versionName> (<versionCode>)

| Release owner | Target date | Track plan | G5 decision |
|---|---|---|---|
| <name> | YYYY-MM-DD | Internal → closed → production (staged) | <date, approver> |

## Build
- [ ] Built by CI from the tag `v<versionName>`
- [ ] `versionCode` higher than every published build
- [ ] Release build type: R8 and resource shrinking on; not debuggable; debug tools excluded
- [ ] Signed with the upload key from CI secrets; Play App Signing enabled
- [ ] Mapping file archived, and uploaded to Play Console and the crash reporter
- [ ] Baseline Profile included

## Play Console
- [ ] Target API level meets Play's current requirement
- [ ] Data safety form matches the data inventory, including SDKs
- [ ] Sensitive permissions declared and justified
- [ ] Content rating and privacy policy URL set; account-deletion link if the app has accounts
- [ ] Store listing, phone and tablet screenshots, and release notes for each locale

## Readiness
- [ ] G5 go decision recorded; test summary report approved
- [ ] Feature flags set; kill switches tested; minimum-version config ready
- [ ] Dashboards and alerts live; on-call owner named
- [ ] Support team briefed; known issues documented

## Rollout
| Step | Track / % | Earliest date | Halt if… | Decision |
|---|---|---|---|---|
| 1 | Internal | | Any S1 defect | |
| 2 | Closed testing | | Crash rate > <n>% | |
| 3 | Production 1% → 5% → 20% → 50% → 100% (≥ 24 h per step) | | Crash rate > <n>%, ANR rate > <n>%, KPI drop > <n>% | |

On a halt:
1. Pause the rollout in Play Console.
2. Disable the feature flag or kill switch.
3. Fix forward with a new `versionCode`.

## Hypercare (<n> days)
- [ ] Daily check of vitals, crashes, store reviews and support tickets; findings logged

## Handover and sign-off
- [ ] Runbook, dashboards, open defects and known limitations handed over to <maintenance owner>
- [ ] RTM closed; lessons learned recorded

| Role | Name | Decision | Date |
|---|---|---|---|
