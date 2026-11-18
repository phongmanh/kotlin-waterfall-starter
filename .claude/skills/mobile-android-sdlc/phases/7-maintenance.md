# Phase 7: Maintenance
**Gate:** each change runs a small gated cycle: CR → design delta (G3-lite) → G5 → staged release
**Deliverables:** vitals reviews, [change requests](../templates/change-request.md), hotfix releases, [postmortems](../templates/postmortem.md) for S1 incidents, updated RTM and docs
**Load:** [review-checklist](../reference/review-checklist.md), [performance-reliability](../reference/performance-reliability.md), plus the phase files the change's size calls for

## Goal
Keep the app stable, secure and compliant as Android, Google Play, devices and dependencies change. Evolve it without breaking what works.

## Activities
1. **Monitor.**
   - Weekly: Android vitals (crash and ANR rates overall and on the worst device models, startup, slow frames), crash reports, store reviews, KPIs.
   - Each release: compare against the previous release.
2. **Triage** by severity, with a response time for each:
   - S1 (crash spike, data loss, security issue): run the incident path below now.
   - S2: next release.
   - S3 and S4: backlog.
3. **Incident and hotfix path** (S1).
   1. **Contain:** halt the staged rollout and switch off the feature's kill switch.
   2. **Communicate:** tell product and support what is affected and when to expect a fix. Update them until it's resolved.
   3. Branch from the release tag.
   4. Make a minimal fix, with a test that failed before the fix.
   5. Expedited review.
   6. G5-lite: the fix plus a regression subset.
   7. Staged rollout, with a higher `versionCode`. A store release can't be rolled back.
   8. Merge back to `main`.
   9. Within a week, write a blameless [postmortem](../templates/postmortem.md): fix the system, not the person. Its action items get owners and dates, and become CRs or tickets.
4. **Change requests.** Every new feature, or change to baselined behaviour, starts with a CR: impact via the RTM, then a decision.
   - A small change runs design delta → implement → test → release.
   - A big one runs the full lifecycle in a new workspace.
5. **Yearly platform update.** For each new Android release:
   - read its behaviour changes and test the app on it;
   - raise `targetSdk` before Play's annual deadline (usually in August);
   - review `minSdk` against audience data.
6. **Dependencies.**
   - Automated update PRs every month (e.g. Renovate or Dependabot).
   - Security patches immediately.
   - Remove libraries that are no longer used.
7. **Tech debt.** Keep a ranked debt list, and reserve a fixed share of each release for it (e.g. 15–20%).
8. **Documentation.** When the code changes, update the architecture document, ADRs and feature designs in the same PR.
9. **End of life.** Retire a feature or an old version with notice:
   1. switch the flag off;
   2. remove the code;
   3. raise the minimum supported version;
   4. clean up the backend.

## Checklist per release
- [ ] Every change in scope has an approved CR; RTM updated
- [ ] Regression suite and affected NFR tests passed
- [ ] `targetSdk` and dependencies within policy
- [ ] Release checklist completed; staged rollout with halt criteria
- [ ] Every S1 since the last release has a postmortem, and its action items are tracked

## Pitfalls
- **Hotfixes that skip tests** and cause the next incident.
- **Postmortems that blame a person,** or action items with no owner or date, so the same incident happens again.
- **Missing the target-SDK deadline,** after which the app can't publish updates.
- **Letting dependencies age** until one update becomes a migration project.
- **Docs that stop matching the code** after the first year.
