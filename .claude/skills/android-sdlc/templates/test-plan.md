# Test plan: <App or feature>

| Version | Status | QA lead | Approvers |
|---|---|---|---|
| 0.1 | Draft | <name> | <product owner, tech lead> |

## 1. Scope
- **In scope:** <FR and NFR IDs>
- **Out of scope:** <…>
- **Regression scope** (for a feature): <…>

## 2. Levels and tools
| Level | Scope | Tools | Owner | When |
|---|---|---|---|---|
| Unit | Domain, data, ViewModels | JUnit, coroutines-test, Turbine, fakes | Developers | Every PR |
| Integration | Room, API, migrations | Room testing, MockWebServer | Developers | Every PR or nightly |
| UI + screenshot | Critical flows; key screens | Compose UI test; Roborazzi | Developers | Nightly |
| System | End to end on the device matrix | Device farm + manual | QA | Phase 5 |
| Acceptance | Must FRs | Play internal or closed track | Product owner, pilot users | Phase 5 |

## 3. Device matrix
| Device or emulator | Android version | Why |
|---|---|---|
| <low-end, e.g. 2–3 GB RAM> | minSdk | Reference device for performance |
| <popular mid-range OEM> | <most common version> | Audience share |
| <latest Pixel> | Latest Android | New behaviour changes |
| <tablet> | Recent | Large screen |
| <foldable> | Recent | Postures and resizing |

## 4. NFR tests
| NFR ID | Test | Method / tool | Target | Result |
|---|---|---|---|---|
| NFR-PERF-01 | Cold start | Macrobenchmark on the reference device | | |

## 5. Acceptance outline
| AT ID | FR | Scenario (Given / When / Then) | Result |
|---|---|---|---|

## 6. Environments and data
- Mock server
- Staging backend
- Test accounts
- Synthetic test data (no production PII)

## 7. Entry and exit criteria
| Level | Entry | Exit |
|---|---|---|
| System | G4 approved; RC installed | All `ST-` tests run; no open S1/S2 defects |
| Acceptance | System exit criteria met | Product owner signs off |

## 8. Defect severity
| Severity | Meaning |
|---|---|
| S1 | Crash, data loss or security issue |
| S2 | A Must FR is broken, with no workaround |
| S3 | A workaround exists |
| S4 | Cosmetic |

---

## Test summary report (Phase 5)
| Level | Planned | Run | Passed | Failed | Blocked |
|---|---|---|---|---|---|

- **NFR results vs targets:** <table or link>
- **Open defects:** S1 <n> · S2 <n> · S3 <n> · S4 <n> (accepted: <list>)
- **Residual risks:** <…>
- **Recommendation:** Go / Go with conditions / No-go, because <reason>
