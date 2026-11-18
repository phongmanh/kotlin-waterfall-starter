# Phase 1: Requirements
**Gate:** G1 Requirements baseline
**Deliverables:** [requirements](../templates/requirements.md), acceptance outline (in the [test plan](../templates/test-plan.md)), [RTM](../templates/rtm.md), [STATUS](../templates/status.md)
**Load:** [ui-ux](../reference/ui-ux.md), [security-privacy](../reference/security-privacy.md) (for the MASVS level, the data inventory and the store disclosures), [platform-integration](../reference/platform-integration.md) (for platform differences that affect requirements)

## Goal
Agree on what the app must do on Android and iOS, and how well, in terms a tester can verify on each platform. No design yet, except constraints the stakeholders impose.

## Entry criteria
- A sponsor and a product owner are named.
- The problem and the target users are known, at least roughly.

## Activities
1. **Brief.** Capture:
   - the problem;
   - goals with measurable KPIs (e.g. "60% of new users finish onboarding"), per platform where they differ;
   - target users and their platform split;
   - what is in and out of scope, including which platforms (desktop and web are out unless stated);
   - constraints: deadline, budget, team (Android, iOS and Kotlin skills), mandated backend or SDKs;
   - approvers and top risks.
2. **Functional requirements.**
   - Write user stories, each with an ID (`FR-nnn`), a MoSCoW priority, its platforms (Both, `[Android]` or `[iOS]`) and Given/When/Then acceptance criteria.
   - Default to platform parity. Every platform-only requirement states why (an OS capability, a store rule, a business decision).
   - Cover the unhappy paths: offline, slow network, permission denied (and on iOS, denied for good), empty data, session expired, Android process death, iOS termination in the background.
3. **Non-functional requirements.** Each one gets a target per platform, the condition it's measured under, and a verification method. These NFRs are almost always needed:

   | Attribute | Example target (agree the real one) | Verified by |
   |---|---|---|
   | PERF startup | Cold start p90 ≤ 1.5 s on the reference low-end Android device and ≤ 1.5 s on the reference iPhone | Macrobenchmark; Xcode Instruments / Organizer |
   | PERF smoothness | Slow frames ≤ 5% (Android); hitch rate below Apple's "good" threshold (iOS) while scrolling key lists | Macrobenchmark, Android vitals; Instruments, MetricKit |
   | REL stability | Crash and ANR rates below Play's bad-behaviour thresholds; crash-free sessions ≥ 99.8% on iOS | Android vitals; crash reporter, Xcode Organizer |
   | REL offline | Saved content readable offline; writes queued and synced later on both platforms | System test |
   | SIZE | Download size ≤ 20 MB (Android) and ≤ 40 MB (iOS) | Play Console and App Store Connect size reports |
   | COMPAT | `minSdk` and iOS deployment target from audience data; Play's required `targetSdk`; phones, tablets, foldables, iPads as agreed | Device matrix |
   | A11Y | Usable with TalkBack and VoiceOver and at the largest text size; touch targets ≥ 48 dp; contrast ≥ 4.5:1 | Accessibility test pass on both platforms |
   | I18N | Listed locales; RTL yes/no | Pseudo-locale tests on both platforms |
   | SEC | MASVS-L1, or L2 for finance, health or identity data; +R if tampering is a risk | MASVS checklist on both platforms |
   | PRIV | Data minimisation; consent before analytics; ATT where tracking applies; in-app account deletion | Privacy review |
   | MAINT | Lint, detekt and SwiftLint clean; unit-test coverage floor; share of code in `commonMain` | CI |
4. **Platform scope.**
   - Android `minSdk` and the iOS deployment target, each chosen from the audience's OS distribution;
   - form factors and orientations on each platform (phones, Android tablets and foldables, iPad);
   - locales and distribution countries;
   - platform extras and whether they are in scope: widgets, Wear OS, Apple Watch, App Clips, Live Activities (usually not, and usually native code).
5. **Store constraints** that shape requirements. Check the current store policies and record what applies:
   - payments for digital goods (in-app purchase rules differ per store and country);
   - sign-in (an app that offers third-party sign-in on iOS must offer an equivalent privacy-focused option such as Sign in with Apple);
   - account deletion inside the app;
   - content and age-rating rules.
6. **Permissions inventory.** For each protected resource: why it's needed, when it's requested, what happens if it's denied, the Android permission and the iOS usage-description key. Prefer options that need no permission: the photo pickers, coarse or approximate location, Credential Manager and AuthenticationServices.
7. **Data inventory.** For each type of data collected: purpose, where it's stored, who it's shared with (including SDKs), how long it's kept, and whether it's used for tracking. This feeds the Play Data safety form, the App Store privacy details, the iOS privacy manifest and the threat model.
8. **External interfaces.**
   - Backend APIs: owner, contract status, environments.
   - Third-party SDKs, and whether each has an Android, an iOS and a KMP option.
   - Deep links, push notifications (FCM, APNs).
   - **Store accounts:** a Google Play developer account and an Apple Developer Program membership. An organisation's Apple enrollment can take weeks (it needs a D-U-N-S number), so start it now.
9. **Acceptance outline.** Write one `AT-` scenario per Must story in the test plan, run on both platforms unless the story is platform-tagged.
10. **Validate.** Walk through the requirements with the product owner, an Android developer, an iOS developer, QA and security. Each requirement must be clear, testable, necessary, and consistent with the others.
11. **Baseline.**
    - Create the RTM rows.
    - Resolve the open TBDs, or accept them explicitly.
    - Ask for sign-off.

## Exit checklist (G1)
- [ ] Every requirement has an ID, a priority, its platforms and testable acceptance criteria
- [ ] Every platform-only requirement states why
- [ ] Every NFR has a number per platform, a condition and a verification method
- [ ] Permissions and data inventories complete for both platforms; MASVS level chosen
- [ ] `minSdk`, the iOS deployment target, form factors and locales agreed
- [ ] Store constraints (payments, sign-in, account deletion) checked against current policies
- [ ] Both store accounts exist, or their set-up is a tracked risk
- [ ] No open TBD blocks a Must requirement
- [ ] Acceptance outline covers every Must requirement; RTM created
- [ ] Approved by the product owner and the tech lead; baseline tagged

## Pitfalls
- **Assuming iOS behaves like Android:** background work that may never run, permissions asked only once, no back button, no state restoration after termination.
- **Unmeasurable NFRs** like "fast", "secure" or "native-feeling", which nobody can test.
- **Silent platform gaps.** A feature that "will come to iOS later" without a requirement tag and a date.
- **Finding a store rule at review time:** digital purchases outside in-app purchase, missing Sign in with Apple, no in-app account deletion.
- **An SDK with no iOS version,** discovered after the design depends on it.
- **Choosing `minSdk` or the deployment target by habit** instead of from audience data.
- **Writing the design** (screens, libraries) into the requirements.
