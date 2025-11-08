# Task T005 — GHCR Auth & Release-Build Pipeline Readiness

## Status
- Status: Proposed (plan pending)
- Owner: TBD
- Links: _(Plan folder will be created once scheduled)_

## Background
We want to ship beta images from GitHub Actions, but matrix targets that depend on
`ghcr.io/devcontainers/images/universal:2-linux` currently fail without GHCR authentication.
A full multi-arch build/test/push pipeline requires logging into GHCR with secrets, running Bake,
running smoke tests, and pushing tags automatically.

## Goals & Deliverables
1. Define required GHCR scopes (likely `read:packages`, `write:packages`) and document how to store
   PATs/credentials for both CI and local use.
2. Author or extend GitHub Actions workflows that:
   - Log into GHCR before builds.
   - Run `docker buildx bake` for the desired matrix (at least act/universal/ubuntu × cline/codex/
     factory_ai_droid).
   - Execute smoke tests (`scripts/test.sh`) and collect logs/artifacts.
   - Push resulting images/tags to GHCR for beta consumers.
3. Update README/task docs with instructions for triggering the pipeline, rotating secrets, and
   troubleshooting auth failures.

## Out of Scope
- Final GA release process (versioning semantics, release notes). This task focuses on enabling the
  beta-quality pipeline with proper authentication.

## Dependencies & Inputs
- Secrets management policies (where PATs live, who rotates them).
- Existing Bake/test scripts from T002/T003.

## Open Questions
- Should the workflow run on every push, only on tagged releases, or manually via workflow dispatch?
- Do we need separate builders per architecture, or can we rely on QEMU emulation in Actions?

## Next Steps
- When scheduled, create the `plan/` structure and link to any GitHub issue tracking the pipeline work.
