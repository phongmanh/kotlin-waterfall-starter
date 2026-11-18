# Phase 7: Maintenance
**Gate:** each change runs a small gated cycle: CR → design delta (G3-lite) → G5 on both platforms → staged release in both stores
**Deliverables:** health reviews, [change requests](../templates/change-request.md), hotfix releases, updated RTM and docs
**Load:** [review-checklist](../reference/review-checklist.md), [performance-reliability](../reference/performance-reliability.md), plus the phase files the change's size calls for

## Goal
Keep the app stable, secure and compliant as Android, iOS, Kotlin, Compose Multiplatform, both stores, devices and dependencies change. Evolve it without breaking what works on either platform.

## Activities
1. **Monitor.**
   - Weekly, per platform: crash, ANR and hang rates, startup, slow frames and hitches, reviews in both stores, KPIs.
   - Each release: compare against the previous release on each platform.
2. **Triage** by severity, with a response time for each:
   - S1 (crash spike, data loss, security issue): hotfix now.
   - S2: next release.
   - S3 and S4: backlog.

   A defect in shared code is fixed once and released on both platforms.
3. **Hotfix path.**
   1. Branch from the release tag.
   2. Make a minimal fix, with a test.
   3. Expedited review.
   4. G5-lite on both platforms: the fix plus a regression subset.
   5. Staged rollout on Android; on iOS, an expedited App Review if needed, then release.
   6. Merge back to `main`.
4. **Change requests.** Every new feature, or change to baselined behaviour, starts with a CR: impact via the RTM, then a decision.
   - A small change runs design delta → implement → test → release.
   - A big one runs the full lifecycle in a new workspace.
5. **Yearly platform updates.**
   - **Android:** for each new Android release, read its behaviour changes and test the app on it; raise `targetSdk` before Play's annual deadline (usually in August).
   - **iOS:** test on each iOS beta from its announcement (usually June) so the app is ready on release day (usually September); build with the Xcode and SDK versions Apple requires for uploads (usually enforced each spring).
   - Review `minSdk` and the iOS deployment target against audience data.
6. **Toolchain.** Upgrade Kotlin, Compose Multiplatform, AGP and Xcode together, following JetBrains' compatibility table; never upgrade Xcode on CI without checking it. One upgrade PR per toolchain step, tested on both platforms.
7. **Dependencies.**
   - Automated update PRs every month (e.g. Renovate or Dependabot), for Gradle and iOS dependencies.
   - Security patches immediately.
   - Remove libraries that are no longer used.
8. **Signing and accounts.** Track the expiry of Apple certificates, provisioning profiles and push keys, and the renewal of the Apple Developer Program membership. An expired certificate blocks the next release; an expired membership removes the app from sale.
9. **Tech debt.** Keep a ranked debt list, and reserve a fixed share of each release for it (e.g. 15–20%). Platform code that grew business logic is debt.
10. **Documentation.** When the code changes, update the architecture document, the platform matrix, ADRs and feature designs in the same PR.
11. **End of life.** Retire a feature or an old version with notice:
    1. switch the flag off;
    2. remove the code;
    3. raise the minimum supported version on both platforms;
    4. clean up the backend.

## Checklist per release
- [ ] Every change in scope has an approved CR; RTM updated
- [ ] Regression suite and affected NFR tests passed on both platforms
- [ ] `targetSdk`, the Xcode/SDK version, the toolchain and dependencies within policy
- [ ] Signing material valid for at least the next release cycle
- [ ] Release checklist completed; staged rollout and phased release with halt criteria

## Pitfalls
- **Hotfixes that skip tests** and cause the next incident.
- **Fixing shared code for one platform** and shipping the regression on the other.
- **Missing a store deadline:** Play's target-SDK date, or Apple's minimum Xcode/SDK for uploads. Either one blocks updates.
- **Toolchain drift:** an Xcode update on CI that the Kotlin version doesn't support yet.
- **Letting dependencies age** until one update becomes a migration project.
- **Docs that stop matching the code** after the first year.
