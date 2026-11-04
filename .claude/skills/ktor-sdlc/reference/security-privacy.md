# Security & privacy reference

Organised around the OWASP API Security Top 10, with the OWASP ASVS level chosen in Phase 1:
- **L1** is the minimum for every service.
- **L2** applies to any service that handles personal, financial, health or other sensitive data, which means most backends behind a mobile app.
- **L3** applies to critical systems (e.g. payments, medical devices) and needs an ADR with a security specialist.

Verify the level in Phase 5. The code for the controls is in [code-patterns.md](code-patterns.md).

## The ground rule for secrets
- **Secrets live in a secret manager** (cloud secret manager, Vault, Kubernetes secrets backed by one) and reach the process as environment variables or mounted files at runtime.
- **Never in Git, images, logs, tickets or error messages.** `application.yaml` names the variable with no default value; config classes holding secrets override `toString()`.
- **Rotate them.** Database passwords, webhook secrets and API keys have an owner and a rotation date; the service reads them at start, so rotation is a redeploy.
- **Least privilege.** The service's database user owns no schema in production: it can read and write its tables, not drop them. The migration job uses a separate user with DDL rights.

## OWASP API Security Top 10
| Risk | Control in a Ktor service | Verified by |
|---|---|---|
| API1 Broken object-level authorisation | Every service method takes the `Caller` and checks ownership or membership of the object; another user's object is a 404 | The 404 case in each endpoint's route tests; authorisation matrix tests in Phase 5 |
| API2 Broken authentication | Tokens only from the identity provider; signature, issuer, audience and expiry verified against the JWKS; short-lived access tokens; no API keys for users | Route tests with wrong audience, wrong issuer and expired tokens |
| API3 Broken object-property-level authorisation | Separate request and response DTOs per endpoint; no domain model or row serialized; no `receive<Map<…>>` | Review; contract check |
| API4 Unrestricted resource consumption | RequestBodyLimit; maximum page size; RateLimit per caller; timeouts on queries and outbound calls; limits on uploads and batch sizes | Tests at the limits; load tests |
| API5 Broken function-level authorisation | Roles checked in the service for privileged operations; admin endpoints in a separate route group with their own authentication | Route tests with a non-admin token |
| API6 Unrestricted access to sensitive business flows | Per-account and per-device limits on sign-up, password reset, OTP, checkout; bot detection or app attestation (Play Integrity, App Attest) where abuse is likely | Abuse-case tests; monitoring |
| API7 Server-side request forgery | No fetching of client-supplied URLs; where it's a feature, an allow-list of hosts and schemes, no redirects, internal ranges and cloud metadata endpoints blocked | Tests with internal addresses |
| API8 Security misconfiguration | Development mode off; no stack traces in responses; security headers; CORS allow-list or no CORS; TLS only; default credentials removed | DAST (e.g. ZAP) in Phase 5; config review |
| API9 Improper inventory management | Every endpoint in the OpenAPI contract with an owner; old versions have a sunset date; no undocumented debug routes | Contract check; route listing vs contract |
| API10 Unsafe consumption of APIs | Responses from third parties validated and size-limited; timeouts; their errors mapped, not passed through | Adapter tests with `MockEngine` |

## Authentication and sessions
- **Bearer tokens (JWT) from an OpenID Connect provider** are the default for mobile and service clients ([code](code-patterns.md#authentication)).
  - Verify the signature with keys from the provider's JWKS, cached and rate-limited; accept only the expected algorithms (asymmetric, e.g. RS256 or ES256).
  - Verify `iss`, `aud` and `exp`, with a small clock-skew leeway (e.g. 30 s).
  - The subject (`sub`) is the user ID; roles and scopes come from agreed claims.
- **Service-to-service calls** use their own credentials (client-credentials tokens, or mTLS inside the mesh), never a user's token passed along without a check.
- **Browser clients:** prefer a backend-for-frontend with cookie sessions (`Sessions` plugin) over tokens in browser storage. Cookies are `Secure`, `HttpOnly`, `SameSite=Lax` or `Strict`; state-changing requests need CSRF protection.
- **Passwords** (only if the service must store them, which an identity provider avoids): Argon2id with OWASP's parameters; never a fast hash. Rate-limit and monitor sign-in.
- **Rotating refresh tokens** (only if the service issues its own, which an identity provider avoids): random, at least 256 bits, stored as a hash, single use, and a used token that comes back revokes the whole sign-in (reuse detection). Design for the case where the same token is sent twice on purpose:
  - **A browser reload races the refresh.** A web app that refreshes on page load and is reloaded mid-refresh loses the answer: the server has rotated the token, the cookie never arrives, and the new page sends the old token, which reads as theft and signs the user out. Taking turns across tabs (Web Locks, `BroadcastChannel`) doesn't help, because a page's lock is released when it unloads; `fetch(…, {keepalive: true})` only narrows the window, and a cold start widens it.
  - **Give a short grace period on the server:** a used token presented again within a few seconds (a setting, 0 = strict; around 10 s) of its use, while the session is live, gets a **fresh** sibling token. The service can't replay the first answer, since it keeps only hashes and never stores tokens for replay. Once one sibling is used, the others stop working; a child already used, an expired window or a cap (e.g. 3 swaps) means it's reuse again. Count the window from the server's first use, take the row lock in one `UPDATE … RETURNING`, and count grace swaps in a metric.
  - **One lock order for every refresh:** the parent's row first (using a child closes the parent's grace, e.g. sets its swap count to the cap), then the token's, then its siblings'. Locking the token first and the parent second lets two sibling refreshes deadlock; a `NOT EXISTS (used child)` check instead of the parent lock misses a child used concurrently. Test the race: several grace swaps at once, and a child's use racing its parent's swaps, answer only 200 or 401.
  - Decide this in the design, with the trade-off written down (a thief who replays within the window isn't caught), not after a client's testing finds the sign-outs.

## Input and output
- **Validate everything that crosses the boundary:** types and shapes by deserialization into DTOs, values by RequestValidation (length, format, range, allow-lists), rules by the service.
- **SQL only through Exposed's DSL** or bound parameters. Never build SQL strings from input; sort fields come from an allow-list.
- **JSON limits:** the body size limit covers deeply nested or huge payloads; collection sizes in requests are validated.
- **File uploads** (if any): a size limit, a content check (magic bytes, not the extension), a malware scan, storage in an object store under a generated name, never on the local disk or served from the app's domain.
- **Output encoding.** The API returns JSON only. Anything the server renders (emails, PDFs, HTML) encodes user content for its context.

## Transport and headers
- **TLS 1.2+ (prefer 1.3) at the edge.** The service usually terminates TLS at a load balancer or ingress; traffic behind it stays in a private network, or uses mTLS where the threat model requires it.
- **Forwarded headers.** Install `XForwardedHeaders` (or `ForwardedHeaders`) only when a proxy you control overwrites them; otherwise any client can spoof its IP address, which also breaks rate limiting.
- **Headers:** `Strict-Transport-Security` (HSTS), `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`; `Cache-Control: no-store` on responses with personal data.
- **CORS** only for browser clients, with an allow-list of origins from configuration. Never `anyHost()`, never credentials with a wildcard.

## Data protection
- **Data classification** from Phase 1 decides the controls per field: public, internal, personal, sensitive.
- **Encryption at rest** for every database, volume and backup (managed keys). Field-level encryption or tokenisation for the most sensitive fields (e.g. government IDs), with keys in a KMS (L2+).
- **IDs** are non-sequential (UUID v7), so they can't be enumerated.
- **Backups** are encrypted, copied to another account or region, and restore-tested.

## Logging and audit
- **Never log** tokens, passwords, secrets, full request or response bodies, or personal data. Log IDs, codes and counts.
- **Redact in the logging layer** (e.g. a Logback masking pattern for `Authorization` headers and known fields), not by developer discipline alone.
- **Audit log** for security-relevant events: sign-in failures, permission changes, access to sensitive records, admin actions, data exports. Who, what, when, from where, and the call ID. Kept separate from application logs, tamper-evident, retained per policy.

## Supply chain
- **Dependencies:** versions only from the version catalog; automated update PRs; a dependency vulnerability scan in CI (e.g. OWASP Dependency-Check or the platform's scanner) that fails on high and critical findings.
- **Image:** a minimal base (distroless or a slim JRE), running as a non-root user with a read-only root filesystem; scanned in CI (e.g. Trivy); built once and promoted by digest.
- **Provenance:** an SBOM (e.g. CycloneDX) and a signed image for each release.
- **CI secrets** are scoped to the jobs that need them; pull requests from forks get none.

## Privacy
- **Minimise.** Collect only what a requirement needs; the data inventory lists each personal field, its purpose and its retention.
- **Retention.** A scheduled, idempotent job deletes or anonymises data past its retention period.
- **Data-subject rights.** Endpoints or runbooks for access, export and erasure, including backups and downstream copies, within the legal deadline.
- **Residency.** Data stays in the regions the requirements name; check where logs, traces and backups go too.
- **Pseudonymised analytics.** Events carry a pseudonymous ID, never an email or a name.
- **Compliance mapping** (GDPR, HIPAA, PCI-DSS, SOC 2): each applicable control maps to a requirement and a test. Reduce scope where possible; e.g. card data goes straight to a payment provider and never touches the service.

## Quick check for reviewers
- A new endpoint outside `authenticate`, or without an object-level check in its service method?
- A domain model, an Exposed row or a `Map` serialized as a response, or received as a request?
- SQL built from strings? A sort or filter field not on an allow-list?
- A secret, token or personal data in code, config defaults, logs or error responses?
- A collection without a maximum page size, or an outbound call without a timeout?
- A client-supplied URL fetched by the server?
- A new dependency without a reason, or with known vulnerabilities?
- A new personal data field without a data-inventory entry and a retention rule?
