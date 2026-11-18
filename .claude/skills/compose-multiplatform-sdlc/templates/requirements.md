# Requirements: <App or feature>

| Version | Status | Owner | Approvers |
|---|---|---|---|
| 0.1 | Draft | <product owner> | <product owner, tech lead> |

## 1. Brief
- **Problem:** <who has which problem today>
- **Goals and KPIs:** <measurable, e.g. "D30 retention ≥ 25% on each platform">
- **Target users:** <personas, their Android/iOS split, the devices they use, accessibility needs>
- **In scope:** <…>
- **Out of scope:** <…; e.g. desktop and web targets, Apple Watch>
- **Constraints:** <deadline, budget, team skills (Kotlin, Android, iOS), mandated backend or SDKs, compliance>
- **Top risks:** <see the STATUS risk register>

## 2. Functional requirements
Platforms: **Both** unless a requirement is tagged `[Android]` or `[iOS]`. A platform-only requirement states why.

| ID | User story | Priority (M/S/C/W) | Platforms | Acceptance criteria (Given / When / Then) |
|---|---|---|---|---|
| FR-001 | As a <user>, I want <goal>, so that <value> | M | Both | Given … when … then …<br>Offline: …<br>Error: …<br>Permission denied: … |

## 3. Non-functional requirements
| ID | Requirement | Android target and condition | iOS target and condition | Verified by |
|---|---|---|---|---|
| NFR-PERF-01 | Cold start | p90 ≤ <n> s on <reference Android device> | p90 ≤ <n> s on <reference iPhone> | Macrobenchmark; Instruments / Xcode Organizer |
| NFR-PERF-02 | Scrolling | Slow frames ≤ <n>% | Hitch rate ≤ <n> ms/s | Macrobenchmark; Instruments |
| NFR-REL-01 | Stability | Crash rate < <n>% and ANR rate < <n>%, below Play's thresholds | Crash-free sessions ≥ <n>% | Android vitals; crash reporter |
| NFR-REL-02 | Offline | <what works offline> | Same | System test |
| NFR-SIZE-01 | Download size | ≤ <n> MB | ≤ <n> MB | Store size reports |
| NFR-A11Y-01 | Accessibility | TalkBack; 200% font; 48 dp targets; 4.5:1 contrast | VoiceOver; largest text size; same targets and contrast | Accessibility test pass |
| NFR-I18N-01 | Languages | <locales>; RTL <yes/no> | Same | Pseudo-locale tests |
| NFR-SEC-01 | Security level | MASVS-<L1/L2> | Same | MASVS checklist |
| NFR-PRIV-01 | Privacy | <consent, retention, account deletion> | Same, plus ATT if tracking | Privacy review |
| NFR-MAINT-01 | Maintainability | Lint, detekt and SwiftLint clean; coverage ≥ <n>% in domain and ViewModels; <n>% of code in `commonMain` | — | CI |

## 4. Platforms and devices
| Item | Android | iOS |
|---|---|---|
| Minimum OS | minSdk <n> (audience data: <source>) | iOS <n> (audience data: <source>) |
| Target | Play's required targetSdk | Apple's required Xcode / SDK |
| Form factors | Phone · Tablet · Foldable | iPhone · iPad (in or out of scope) |
| Orientations | Portrait · Landscape | Portrait · Landscape |
| Reference low-end device | <model, RAM> | <model, RAM> |
| Extras | Widgets, Wear OS (in or out of scope) | Widgets, Apple Watch, App Clips, Live Activities (in or out of scope) |
| Distribution | <countries>; Google Play only, or other stores too | <countries>; App Store |

## 5. Store constraints
| Topic | Google Play | App Store | Affects |
|---|---|---|---|
| Payments for digital goods | <rule that applies> | <rule that applies> | FR-… |
| Sign-in options | — | <equivalent privacy-focused option required if third-party sign-in is offered> | FR-… |
| Account deletion | In the app and through a web link | In the app | FR-… |
| Age rating and content | <…> | <…> | |

## 6. Permissions inventory
| Resource | Why (FR) | When requested | If denied | Android permission | iOS usage-description key | Alternatives considered |
|---|---|---|---|---|---|---|
| e.g. Notifications | FR-010 reminders | When the first reminder is set | Reminders off; a banner in settings | `POST_NOTIFICATIONS` | — (system prompt) | — |
| e.g. Camera | FR-012 scan receipts | On the first scan | Manual entry | `CAMERA` | `NSCameraUsageDescription` | Photo picker |

## 7. Data inventory
This section feeds the Play Data safety form, the App Store App Privacy details and the iOS privacy manifest.

| Data type | Purpose | Stored (device / server) | Encrypted | Shared with (including SDKs) | Used for tracking | Retention |
|---|---|---|---|---|---|---|

## 8. External interfaces
| Interface | Owner | Contract (link, status) | Environments | Android | iOS | KMP option |
|---|---|---|---|---|---|---|
| Backend REST API | | OpenAPI <link> | dev / staging / prod | Ktor | Ktor | Yes |
| Push | | | | FCM | APNs | — |
| Third-party SDKs | | | | <SDK> | <SDK> | <yes / no: Swift implementation> |
| Deep links | | | | App Links | Universal Links | Common router |
| Store accounts | | | | Play Console | Apple Developer Program | — |

## 9. Acceptance outline
One `AT-` scenario per Must FR, run on each of its platforms, kept in [test-plan.md](test-plan.md) §5.

## 10. Assumptions and open items
- ASSUMPTION: <…>
- TBD-1: <…>

## 11. Sign-off
| Role | Name | Decision | Date |
|---|---|---|---|
