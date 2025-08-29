# Repository Improvement Backlog — FixMyDocs

Date: 2025-08-29
Scope: Backend (FastAPI/Python), Worker (Celery/Python), Frontend (Next.js/TypeScript)
Sources: Code review across `backend/`, `worker/`, `frontend/`, and docs. Items include acceptance criteria and priorities.
Note: `docs/BUGFIXER.md` remains the canonical bug log; this backlog complements it. Infrastructure/deployment items are grouped at the end.

---

## Priorities
- P0: Critical path breakage or security risk; blocks main flows.
- P1: Important correctness, UX, or maintainability issues.
- P2: Enhancements, optimizations, or nice-to-haves.

---

## P0 — Critical Bugs and Gaps

1) Worker repo validation syntax error
- Evidence: `worker/repo_manager.py` — function `validate_repository` contains a Python syntax error in the for-loop target, preventing import. This breaks the worker pipeline at import time.
- Impact: Worker cannot start; jobs fail.
- Acceptance:
  - Importing `repo_manager.py` in a Python REPL succeeds with no SyntaxError.
  - Unit test executes `validate_repository()` on valid/invalid URLs and returns expected booleans.

2) Patcher duplicate method definitions override logic
- Evidence: `worker/patcher.py` — later duplicate method names shadow earlier implementations (e.g., PR creation/push helpers), effectively disabling real logic at runtime.
- Impact: Commits/PR creation unreliable; job completion stalls.
- Acceptance:
  - Only one canonical implementation per method; no duplicate names.
  - Unit tests prove commit creation and PR creation logic is invoked and returns expected shapes (mocked network).

3) Backend GitHub URL parsing bug
- Evidence: `backend/main.py` — repository URL cleanup uses `.replace("$.git", "")` instead of `.replace(".git", "")`.
- Impact: Incorrect repo names; forks/PRs and cloning may fail.
- Acceptance:
  - Parsing `https://github.com/owner/repo.git` yields `owner/repo`.
  - Tests cover URLs with/without `.git` and SSH forms.

4) Missing GET /api/repos endpoint used by frontend
- Evidence: Frontend pages call `GET /api/repos`, but backend lacks this route.
- Impact: Repos page cannot render user repositories.
- Acceptance:
  - Backend exposes `GET /api/repos` returning a JSON array of user-connected repositories.
  - Frontend renders list without errors and passes an integration test.

5) Worker DB URL validation rejects SQLAlchemy URIs
- Evidence: `worker/worker.py` uses URL checks that reject dialect URIs (e.g., `sqlite:///...`).
- Impact: Local/dev/test environments fail to start.
- Acceptance:
  - Worker accepts standard SQLAlchemy URLs (sqlite, postgres) and starts.
  - Negative tests still reject malformed strings.

6) Webhook signature not verified
- Evidence: `backend/main.py` GitHub webhook handler lacks HMAC signature verification.
- Impact: Security risk; spoofable webhook calls.
- Acceptance:
  - HMAC (X-Hub-Signature-256) verified with shared secret; invalid requests return 401.
  - Unit tests validate both valid and tampered payloads.

7) Tests drifted from code
- Evidence: Some tests import symbols no longer present and/or assume routes that changed.
- Impact: CI signal is unreliable; regressions may slip through.
- Acceptance:
  - Test suite updated to match current public API and passes locally.
  - At least one happy-path e2e for auth→connect repo→run job→status.

---

## P1 — Important Issues and Features

8) FE API client and base URL handling
- Problem: Pages use relative `fetch('/api/...')`, causing SSR/client ambiguity and no central error handling.
- Acceptance:
  - Introduce a tiny typed API client with base URL from env (server/client aware), standardized error handling, and request/response types.
  - Pages import client; integration tests pass.

9) Job cancellation and idempotency
- Problem: No cancellation endpoint; repeated triggers may duplicate work.
- Acceptance:
  - `POST /api/jobs/{id}/cancel` cancels queued/running jobs (best-effort); idempotent job submission by content hash within time window.
  - Unit tests cover duplicate submission and cancel semantics.

10) Unify Job schema across backend and worker
- Problem: Divergent SQLAlchemy models for Job cause drift.
- Acceptance:
  - Shared shape (fields, statuses) and consistent transitions; migrations applied.
  - Tests assert identical enums/columns and transitions.

11) Robust OAuth state/PKCE and session separation from GitHub token
- Problem: App auth token conflated with GitHub access token in places.
- Acceptance:
  - Distinct session token scoped to app; GitHub token stored/used server-side only; state/nonce/PKCE validated.
  - Security tests cover CSRF/nonce failures.

12) Error reporting and traceability
- Problem: Logs lack correlation IDs; user-facing errors are generic.
- Acceptance:
  - Correlation ID on each request/job; structured logs; ErrorBoundary shows friendly messages.
  - Smoketests assert header propagation to worker logs.

13) Rate limiting and basic abuse protection
- Problem: Unlimited hits to sensitive endpoints.
- Acceptance:
  - Lightweight rate limits on auth, webhook, and job create; 429 on excess.
  - Tests verify tokens/IP buckets.

14) Parser hardening for non-Python repos
- Problem: Many stubs; missing language-specific guards.
- Acceptance:
  - Graceful no-op with clear messages for unsupported languages; no crashes on large repos.
  - Tests for JS/TS/MD-heavy repos.

---

## P2 — Enhancements and Cleanup

15) Frontend performance and config cleanup
- Issue: `next.config.ts` experimental `optimizePackageImports` lists unused libs.
- Acceptance:
  - Remove or align list with installed deps; add basic caching headers where appropriate; confirm no warnings on build.

16) Accessibility and SEO improvements
- Acceptance:
  - Pages have unique titles/meta; form controls have labels; links/buttons are distinguishable; axe checks pass in tests.

17) Developer experience
- Acceptance:
  - Pre-commit hooks for lint/test; consistent formatter configs across repos; quick-start scripts for dev/test.

18) Documentation accuracy
- Acceptance:
  - README and docs align with actual endpoints and flows; examples are tested snippets.

---

## Security-Focused Fixes (cross-cutting)
- Verify webhook signatures (P0) and enforce HTTPS in production.
- Rotate and scope secrets; avoid leaking GitHub tokens to client.
- Input validation and output encoding on all user-supplied fields.

---

## Test Strategy
- Unit: parser utils, repo manager, patcher, job manager, auth helpers.
- Integration: backend routes with a temp DB; worker tasks with mocked network.
- E2E: connect repo → run docs job → poll status → verify PR.
- Acceptance: Each backlog item lists explicit pass criteria.

---

## Infra/Operations (deferred specifics)
- Health checks for all services; graceful shutdown for worker.
- Observability: request/job metrics and traces; error budgets.
- CI: run linters, type-checkers, unit/integration tests; artifact build.
- Containers: resource caps and minimal images.

---

## Quick Wins (suggested first passes)
1) Fix `.replace("$.git")` → `.replace(".git")` and add `GET /api/repos`.
2) Remove duplicate methods in `worker/patcher.py` and correct `repo_manager.py` syntax.
3) Relax worker DB URL validation to accept SQLAlchemy URIs.
4) Add HMAC verification to webhook handler.

Each delivers immediate stability and unblocks core flows.

---

## Tracking and Status
- Link items to `docs/BUGFIXER.md` IDs when applicable.
- Update this backlog as issues are addressed; keep `BUGFIXER.md` authoritative for bug counts/status.
