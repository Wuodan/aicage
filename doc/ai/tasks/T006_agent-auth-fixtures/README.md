# Task T006 — Deterministic Agent Auth Fixtures for Tests

## Status
- Status: Proposed (plan pending)
- Owner: TBD
- Links: _(Plan folder will be created once scheduled)_

## Background
CI smoke tests currently stop at agent startup because the CLIs demand API keys, OAuth, or other
credentials. We need a repeatable way to inject dummy-but-valid credentials (or point to free models)
so tests like “agent prints hello world” can run autonomously in GitHub pipelines and locally.

## Goals & Deliverables
1. Enumerate required env vars/config files per agent (Cline, Codex, Factory Droid, future ones) and
   choose non-cost or mock providers for test flows.
2. Provide sample credential bundles (e.g., template `.env`, fake `~/.codex/config.toml`) and update
   scripts/tests to consume them securely (no secrets committed).
3. Update smoke tests/harnesses so they perform a minimal authenticated action (e.g., `codex exec` or
   `cline task`) using those fixtures.
4. Document secret storage/rotation strategy for CI and local dev, including how to avoid leaking
   keys in logs.

## Out of Scope
- Implementing paid-provider integrations; stick to free tiers or mocks suitable for CI.

## Dependencies & Inputs
- Findings from T003 startup captures (Node 20 requirement, API-key login flows).
- Future GHCR pipeline (Task T005) for full CI integration.

## Open Questions
- Do we emulate providers locally (e.g., mock HTTP servers) or rely on official “free” models?
- Where should credential templates live (repo vs. encrypted storage)?

## Next Steps
- Once prioritized, create the plan folder, log research, and coordinate with whoever owns secrets.
