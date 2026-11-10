---
paths:
  - "docs/sdlc/**"
---
# SDLC Documents

Applies to the deliverables of the android-sdlc (`/android-sdlc`), compose-multiplatform-sdlc (`/compose-multiplatform-sdlc`) and ktor-sdlc (`/ktor-sdlc`) workflows under `docs/sdlc/<initiative-slug>/`.

- **Start from `STATUS.md`.** Check the current phase, and confirm the previous gate is approved before writing a later phase's deliverable.
- **Follow the template** of the workflow that owns the workspace, keeping its section order and tables. `STATUS.md` names the skill:
  - ktor-sdlc (a Ktor backend): `.claude/skills/ktor-sdlc/templates/`;
  - compose-multiplatform-sdlc (an Android + iOS app): `.claude/skills/compose-multiplatform-sdlc/templates/`;
  - otherwise: `.claude/skills/android-sdlc/templates/`.
- **Platforms.** In a compose-multiplatform-sdlc workspace, requirements, designs and tests apply to Android and iOS unless tagged `[Android]` or `[iOS]`, and every gate is checked on both.
- **API contract.** In a ktor-sdlc workspace, the OpenAPI contract (`docs/api/openapi.yaml`) is baselined at G3 with the feature designs. Changing it needs a CR, and a breaking change needs a new API version and a deprecation plan.
- **IDs everywhere:**
  - `FR-nnn`;
  - `NFR-<ATTR>-nn`, with the attributes the owning skill lists;
  - test IDs `UT-`/`IT-`/`UI-`/`ST-`/`AT-`, plus `CT-` (contract) in ktor-sdlc workspaces;
  - in ktor-sdlc workspaces, design elements by name: endpoints as `METHOD /path`, tables, events.

  Every new requirement, design element and test gets an `rtm.md` row in the same change.
- **Never invent** numbers, approvals, approver names or sign-off dates. Mark unknowns `TBD-<n>` and assumptions `ASSUMPTION:`, and list both in `STATUS.md`.
- **Baselined documents.** A deliverable whose `STATUS.md` row says Approved is baselined.
  - Change it only through an approved `cr/CR-NNN-<title>.md`.
  - The `guard-sdlc-baseline.py` hook asks the user to confirm before such an edit. Only the user can switch it off (`SDLC_GATE=off` in `.claude/settings.local.json`); the CR rule still holds when it's off.
- **Gate decisions** go only in the `STATUS.md` gate log, and only after the approver has given them in the conversation.
- **Handoff.** `STATUS.md` ends with a `## Handoff` section, rewritten at the end of every session and never baselined. Facts only, ≤ 15 lines (the hook injects at most 30):
  ```markdown
  ## Handoff
  - **Last session:** <date> — <what got done, one line>
  - **State:** <e.g. "G1 awaiting sign-off" · "Phase 4 PR 6 (session) in review">
  - **Next action:** <the exact first step for the next session>
  - **Load:** <files and sections or line ranges to read first>
  - **Inputs:** <where external sources are cached or pinned, with versions and commits>
  - **Waiting on user:** <decision, approval or review, or "nothing">
  ```
- **Keep documents short:** tables and bullets over prose; link instead of repeating.
