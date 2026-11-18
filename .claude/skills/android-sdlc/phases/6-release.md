# Phase 6: Release
**Gate:** G6 Launch accepted
**Deliverables:** completed [release checklist](../templates/release-checklist.md), rollout record, handover pack
**Load:** [performance-reliability](../reference/performance-reliability.md#observability), [security-privacy](../reference/security-privacy.md#privacy)

## Goal
Ship the approved build to Google Play safely and in stages, watch it in production, and hand it over to the team that runs it.

## Entry criteria
- G5 approved, with the go decision recorded.
- Play Console access is in place; the store-listing owner and the on-call owner are named.

## Activities
1. **Build and signing.**
   - CI builds the release AAB from the tagged commit.
   - `versionCode` only goes up; `versionName` follows the release scheme.
   - The upload key lives in CI secrets; Play App Signing holds the app signing key.
   - Archive the R8 mapping file and upload it to Play Console and the crash reporter.
   - CI uploads to Play through the Play Developer API (e.g. Gradle Play Publisher), not by hand.
2. **Play Console.**
   - The Data safety form matches the data inventory, including what SDKs collect.
   - Sensitive permissions (e.g. background location) are declared and justified.
   - The target API level meets Play's current requirement.
   - Content rating, the privacy policy URL, and an account-deletion link if the app has accounts.
   - Store listing, phone and tablet screenshots, and release notes for each locale.
3. **Rollout through tracks.** Internal → closed testing → production. Production uses a **staged rollout**, e.g. 1% → 5% → 20% → 50% → 100%, with at least 24 hours per step.
4. **Halt criteria**, agreed before the rollout starts. For example:
   - the crash or ANR rate goes above its target;
   - a new S1 defect appears;
   - a key KPI drops by more than an agreed percentage.

   On a halt:
   1. Stop the rollout in Play Console.
   2. Switch off the feature flag or kill switch.
   3. Ship a fix forward. A store release can't be rolled back.
5. **Safety nets.**
   - Remote config for the feature flags and kill switches.
   - Each flag has a safe default for when remote config can't load, an owner and a removal date. Remove flags after launch: they are tech debt.
   - Test each kill switch on the release build before the rollout starts.
   - A minimum-supported-version check that prompts a forced update through In-App Updates.
6. **Hypercare** (e.g. 1–2 weeks).
   - Review Android vitals, crash reports, store reviews and support tickets every day.
   - Name the on-call owner.
7. **Handover** to the maintenance team:
   - a runbook covering build, release, disabling a feature through flags, and hotfixes;
   - dashboards and alert owners;
   - open defects and known limitations.
8. **Close.**
   - Finish the RTM (requirement → release).
   - Record lessons learned.
   - Archive the baselines.

## Exit checklist (G6)
- [ ] Rollout reached 100% with no halt criteria hit, or every halt resolved
- [ ] Vitals and KPIs within target during hypercare
- [ ] Mapping files uploaded; dashboards and alerts live
- [ ] Handover accepted by the maintenance owner
- [ ] RTM closed; lessons learned recorded

## Pitfalls
- **Releasing to 100% at once.**
- **Inventing halt criteria** after things have gone wrong.
- **Losing the upload key,** or keeping it on a laptop.
- **A Data safety form that doesn't match** what an SDK actually collects, which leads to a policy strike.
- **No kill switch** for a risky feature.
