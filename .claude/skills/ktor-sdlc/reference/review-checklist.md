# Review checklist

For authors before they ask for a review, and for reviewers. A PR that breaks the PR rules goes back to the author before anyone reviews it line by line.

## PR rules
- **Small and single-purpose.** One concern, ≤ ~400 changed lines (not counting generated files), taken from the feature design's slice plan. A migration and the code that needs it may share a PR only if the migration is expand-only.
- **Branch and title** follow the project's git rules, e.g. `feature/JIRA-123-notes-api` and `JIRA-123: Add notes list endpoint`.
- **The description** covers:
  - what changed and why;
  - the FR IDs and the endpoints (`METHOD /path`);
  - how it was tested;
  - API changes: the contract diff, and whether any change is breaking (it must not be, within a version);
  - migrations: what they do, how long they take on production-sized data, and whether they're backward compatible;
  - risks, and how to roll back (flag, previous image).
- **CI is green before review,** including the contract check and the scans, and the PR has no unrelated reformatting.

## Review order
Feature design → contract diff → tests (do they describe the right behaviour?) → migrations → domain and services → persistence → routes and DTOs → configuration and DI → deployment files.

## Checklist
**Scope and traceability**
- [ ] Matches the approved feature design; nothing unrequested; any deviation has an approved CR
- [ ] FR IDs in the PR; RTM rows updated for the endpoints, tables and tests

**API contract and compatibility**
- [ ] The OpenAPI contract is updated in the same PR, and the generated document matches it
- [ ] Only additive changes within the version: no removed or renamed fields, no new required request fields, no changed types, status codes or error codes
- [ ] Separate request and response DTOs; no domain model or row serialized
- [ ] Errors are problem+json with a stable `code`; collections are paginated with a maximum page size
- [ ] Status codes follow the [API design](api-design.md#resources-and-methods) table (201 + `Location`, 204, 404 for others' resources, 412/428 for conditional updates)

**Architecture**
- [ ] Layer rules hold: no Ktor, Exposed or serialization types in the domain; routes call one service method and never a repository; DTOs and table objects stay in their adapter
- [ ] Code sits in the right feature package or module; no feature reads another feature's tables
- [ ] Dependencies come from Koin; routes receive services as parameters; no `object` singletons holding state
- [ ] Configuration comes from `AppConfig`; no raw `environment.config` reads in classes

**Kotlin**
- [ ] `val` and read-only types; no `!!`; `when` over a sealed type lists every subtype, with no `else`
- [ ] Clear names, small functions, no magic numbers, no dead or commented-out code

**Coroutines and blocking**
- [ ] Nothing blocks a request coroutine: JDBC only inside `transactor.inTransaction`, no `Thread.sleep`, no blocking I/O outside the IO dispatcher
- [ ] No `GlobalScope`, `runBlocking` or hard-coded `Dispatchers`
- [ ] No remote calls or suspension inside a transaction
- [ ] `CancellationException` never swallowed; no broad `catch (e: Exception)` around suspend calls

**Data and migrations**
- [ ] A schema change comes as a new Flyway migration (no edits to applied ones), with the matching table-object change; the schema-drift test passes
- [ ] The migration is backward compatible with the running version (expand → migrate → contract); big indexes use `CONCURRENTLY`
- [ ] Every new query has an index that serves it, checked with `EXPLAIN` on realistic data; no N+1 and no unbounded query
- [ ] Concurrent updates use the version column; transactions are short and cover everything that must be atomic (change, outbox, idempotency record)

**Security and privacy**
- [ ] New routes are inside `authenticate` unless the design says otherwise; the service checks object-level (and, where needed, role) access for the `Caller`
- [ ] Input validated (RequestValidation and service rules); sort and filter fields from an allow-list; no SQL built from strings
- [ ] No secrets, tokens or personal data in code, config defaults, logs, metrics labels or error responses
- [ ] Refresh-token rotation with reuse detection has a tested grace period for a token sent twice by a reload, or a recorded reason for none ([security](security-privacy.md#authentication-and-sessions))
- [ ] Limits in place: body size, page size, rate limits; timeouts on every outbound call
- [ ] New personal data is in the data inventory with a retention rule; new dependencies are justified and scanned

**Reliability and observability**
- [ ] Outbound calls have timeouts; retries only for idempotent requests; failures mapped at the adapter
- [ ] Retried creates are idempotent (`Idempotency-Key`); events go through the outbox
- [ ] Logs from the design are present, with placeholders and no personal data; metrics for new business events; alerts and runbooks updated if behaviour or SLOs change

**Tests**
- [ ] Services: the happy path, each `DomainError`, access by another user, edge cases
- [ ] Routes: the 401 / 400 / 404 / success matrix for each new endpoint, plus 412/428 where they apply
- [ ] Repositories and migrations tested on PostgreSQL (Testcontainers), never H2
- [ ] Tests are deterministic (injected clock and IDs, no sleeps); a bug fix includes a test that failed before the fix

## Giving feedback
- **Label each comment:** **blocker** (must fix), **suggestion** (optional), **question**, or **nit**.
- **Explain why,** and link the rule or pattern.
- **Approve once the blockers are fixed.** Don't hold a PR for nits.
