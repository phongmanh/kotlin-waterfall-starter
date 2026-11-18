# Phase 1: Requirements
**Gate:** G1 Requirements baseline
**Deliverables:** [requirements](../templates/requirements.md), acceptance outline (in the [test plan](../templates/test-plan.md)), [RTM](../templates/rtm.md), [STATUS](../templates/status.md)
**Load:** [ui-ux](../reference/ui-ux.md), [security-privacy](../reference/security-privacy.md) (for the MASVS level and the data inventory)

## Goal
Agree on what the app must do and how well, in terms a tester can verify. No design yet, except constraints the stakeholders impose.

## Entry criteria
- A sponsor and a product owner are named.
- The problem and the target users are known, at least roughly.

## Activities
1. **Brief.** Capture:
   - the problem;
   - goals with measurable KPIs (e.g. "60% of new users finish onboarding");
   - target users;
   - what is in and out of scope;
   - constraints: deadline, budget, team, mandated backend or SDKs;
   - approvers and top risks.
2. **Functional requirements.**
   - Write user stories, each with an ID (`FR-nnn`), a MoSCoW priority and Given/When/Then acceptance criteria.
   - Cover the unhappy paths: offline, slow network, permission denied, empty data, session expired, process death.
3. **Non-functional requirements.** Each one gets a target, the condition it's measured under, and a verification method. These Android NFRs are almost always needed:

   | Attribute | Example target (agree the real one) | Verified by |
   |---|---|---|
   | PERF startup | Cold start p90 ≤ 1.5 s on the reference low-end device | Macrobenchmark |
   | PERF smoothness | Slow frames ≤ 5% while scrolling key lists | Macrobenchmark, Android vitals |
   | REL stability | User-perceived crash and ANR rates below Play's bad-behaviour thresholds (e.g. 1.09% / 0.47%) | Android vitals |
   | REL offline | Saved content readable offline; writes queued and synced later | System test |
   | SIZE | Download size ≤ 15 MB | Play Console size report |
   | COMPAT | `minSdk` from audience data; Play's required `targetSdk`; phones, tablets, foldables | Device matrix |
   | A11Y | Usable with TalkBack and at font scale 200%; touch targets ≥ 48 dp; contrast ≥ 4.5:1 | Accessibility test pass |
   | I18N | Listed locales; RTL yes/no | Pseudo-locale tests |
   | SEC | MASVS-L1, or L2 for finance, health or identity data; +R if tampering is a risk | MASVS checklist |
   | PRIV | Data minimisation; consent before analytics; in-app account deletion | Privacy review |
   | MAINT | Lint and detekt clean; unit-test coverage floor | CI |
4. **Platform scope.**
   - `minSdk`, chosen from the audience's OS distribution;
   - form factors and orientations;
   - locales and distribution countries;
   - whether Wear OS, TV or Auto is in scope (usually not).
5. **Permissions inventory.** For each runtime permission: why it's needed, when it's requested, and what happens if it's denied. Prefer options that need no permission: the photo picker, Credential Manager, coarse location.
6. **Data inventory.** For each type of data collected: purpose, where it's stored, who it's shared with (including SDKs), and how long it's kept. This feeds the Play Data safety form and the threat model.
7. **External interfaces.**
   - Backend APIs: owner, contract status, environments.
   - Third-party SDKs, deep links, push notifications.
8. **Acceptance outline.** Write one `AT-` scenario per Must story in the test plan.
9. **Validate.** Walk through the requirements with the product owner, a developer, QA and security. Each requirement must be clear, testable, necessary, and consistent with the others.
10. **Baseline.**
    - Create the RTM rows.
    - Resolve the open TBDs, or accept them explicitly.
    - Ask for sign-off.

## Exit checklist (G1)
- [ ] Every requirement has an ID, a priority and testable acceptance criteria
- [ ] Every NFR has a number, a condition and a verification method; no number is still marked "(proposed)"
- [ ] Permissions and data inventories complete; MASVS level chosen
- [ ] `minSdk`, form factors and locales agreed
- [ ] No open TBD blocks a Must requirement
- [ ] Acceptance outline covers every Must requirement; RTM created
- [ ] Approved by the product owner and the tech lead; baseline tagged

## Pitfalls
- **Unmeasurable NFRs** like "fast", "secure" or "user-friendly", which nobody can test.
- **Happy paths only.** Android apps fail most often offline, after process death, and when a permission is denied.
- **Choosing `minSdk` by habit** instead of from audience data.
- **Finding out at release time** that the Data safety form contradicts what an SDK collects.
- **Writing the design** (screens, libraries) into the requirements.
