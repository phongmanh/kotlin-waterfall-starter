# Test plan: <App or feature>

| Version | Status | QA lead | Approvers |
|---|---|---|---|
| 0.1 | Draft | <name> | <product owner, tech lead> |

## 1. Scope
- **In scope:** <FR and NFR IDs>, on <Android and iOS>
- **Out of scope:** <…>
- **Regression scope** (for a feature): <…>, on both platforms

## 2. Levels and tools
| Level | Scope | Tools | Runs on | Owner | When |
|---|---|---|---|---|---|
| Unit | Domain, data, ViewModels | kotlin-test, coroutines-test, Turbine, fakes | `commonTest` on the JVM and the iOS simulator | Developers | Every PR |
| Integration | Room, API, migrations, DI graph, platform services | `MockEngine`, in-memory Room, platform test source sets | JVM, iOS simulator, Android device | Developers | Every PR or nightly |
| UI + screenshot | Critical flows; key screens | Common Compose UI tests; Roborazzi; XCUITest smoke test | iOS simulator, Android emulator, JVM | Developers | Nightly |
| System | End to end on both device matrices | Device farms + manual | Release builds | QA | Phase 5 |
| Acceptance | Must FRs | Play internal or closed track; TestFlight | Release builds | Product owner, pilot users | Phase 5 |

## 3. Device matrix
| Platform | Device or simulator | OS version | Why |
|---|---|---|---|
| Android | <low-end, e.g. 2–3 GB RAM> | minSdk | Reference device for performance |
| Android | <popular mid-range OEM> | <most common version> | Audience share |
| Android | <latest Pixel> | Latest Android | New behaviour changes |
| Android | <tablet>, <foldable> | Recent | Large screens, postures and resizing |
| iOS | <oldest supported iPhone, least RAM> | Oldest supported iOS | Reference device for performance and memory |
| iOS | <most common iPhone in the audience> | <most common version> | Audience share |
| iOS | <latest iPhone with ProMotion and Dynamic Island> | Latest iOS | 120 Hz, insets, new behaviour |
| iOS | <iPad> (if in scope) | Recent | Large screen, multitasking |

## 4. NFR tests
| NFR ID | Test | Platform | Method / tool | Target | Result |
|---|---|---|---|---|---|
| NFR-PERF-01 | Cold start | Android | Macrobenchmark on the reference device | | |
| NFR-PERF-01 | Cold start | iOS | Instruments App Launch on the reference iPhone, Release build | | |

## 5. Acceptance outline
| AT ID | FR | Platforms | Scenario (Given / When / Then) | Android result | iOS result |
|---|---|---|---|---|---|

## 6. Environments and data
- Mock server
- Staging backend
- Test accounts, including an App Review demo account
- Synthetic test data (no production PII)

## 7. Entry and exit criteria
| Level | Entry | Exit |
|---|---|---|
| System | G4 approved; both RCs installed | All `ST-` tests run on both platforms; no open S1/S2 defects |
| Acceptance | System exit criteria met | Product owner signs off for each platform |

## 8. Defect severity
| Severity | Meaning |
|---|---|
| S1 | Crash, data loss or security issue |
| S2 | A Must FR is broken, with no workaround |
| S3 | A workaround exists |
| S4 | Cosmetic |

Each defect records its platform; a defect in shared code is re-tested on both.

---

## Test summary report (Phase 5)
| Level | Platform | Planned | Run | Passed | Failed | Blocked |
|---|---|---|---|---|---|---|

- **NFR results vs targets, per platform:** <table or link>
- **Open defects:** Android S1 <n> · S2 <n> · S3 <n> · S4 <n>; iOS S1 <n> · S2 <n> · S3 <n> · S4 <n> (accepted: <list>)
- **Residual risks:** <…>
- **Recommendation:** Android: Go / Go with conditions / No-go; iOS: Go / Go with conditions / No-go, because <reason>
