# Task T002 — Validate llm-agent-dock Builds & Docker Access

> This README is mirrored in `doc/ai/TASK.md`. Keep both in sync so the active task brief is always discoverable.

## Background
- Task T001 delivered the parameterized Dockerfile, Bake matrix, helper scripts, smoke tests, and documentation.
- No real images were built because the container user lacked access to `/var/run/docker.sock`.
- Smoke tests could not run because `bats` was missing. The host will provide `bats` before this task begins.
- The next session must focus on executing the automation end-to-end and documenting how to grant Docker access when working under similar constraints.

## Goals
1. Verify that host prerequisites are satisfied (Docker daemon permissions + `bats`).
2. Execute `scripts/build.sh <tool> <base>` for representative matrix entries (at least one per tool) and capture logs.
3. Run `scripts/test.sh` for every tool using the images produced above; document results and failures.
4. Produce guidance for enabling Docker socket access in constrained environments (or document the escalation path if host changes are required).
5. Update README/plan docs with validated commands, known issues, and any additional troubleshooting notes.

## Scope & Deliverables
- Use the existing matrix: bases (`act`, `universal`, `ubuntu`) × tools (`cline`, `codex`, `factory_ai_droid`).
- At minimum, build `ubuntu`-based images for each tool; stretch goal is full matrix coverage.
- Smoke tests (`tests/smoke/*.bats`) must pass for every tool or have documented blockers.
- Provide build/test logs or summaries in the Feedback section and planning docs.

## Workflow Expectations
1. **S1 Planning & Environment Check** — Create/refresh planning artifacts for T002 (new `doc/ai/plan/` entries or an addendum) capturing prerequisites and risks.
2. **S2 Docker Access Enablement** — Determine whether Docker socket access is already available; if not, outline the exact steps (group membership, rootless Docker, etc.) and work with the host to enable it.
3. **S3 Matrix Builds** — Run `scripts/build.sh` for selected targets (start with `codex ubuntu amd64`) and expand coverage once stable.
4. **S4 Smoke Tests** — Execute `scripts/test.sh <image>` for each tool; include `--tool` filtering to speed up iteration when necessary.
5. **S5 Documentation & Handoff** — Update README, AGENTS, and planning docs with validated commands, log locations, and any long-term lessons.

## Prerequisites & Assumptions
- `bats` should be installed on the host before starting this task (`bats --version` should succeed).
- Docker access is still uncertain. First action is to run `docker info` to confirm permissions; if it fails, capture the error and document the remediation steps.
- Existing automation assumes internet access to npm registries for agent installers; coordinate with the host if additional proxies are required.

## References
- Task T001 artifacts: `doc/ai/tasks/T001_llm-agent-dock-matrix-builder/README.md`.
- Planning/log context: `doc/ai/plan/README.md` and subtask folders S1–S5 (historical reference).
- Automation entry points: `scripts/dev/bootstrap.sh`, `scripts/build.sh`, `scripts/test.sh`.

## Feedback — Open Problems, Questions, Learnings
- **Open Problems**
  - Docker socket access flow is undefined; determine whether adding the user to the `docker` group or enabling rootless Docker is acceptable in this environment.
  - Need a repeatable strategy for running multi-arch builds locally without elevated privileges (consider remote builders or `docker context` usage).
- **Questions**
  - Which registry should host published images once builds succeed? (Currently defaults to `ghcr.io/wuodan/llm-agent-dock`.)
  - Are there SLAs for how many matrix combinations must be built per run (subset vs. entire 9 variants)?
- **Learnings**
  - Capturing prerequisites (like `bats` and Docker group membership) before implementation prevents wasted cycles; bake these checks into bootstrap scripts if feasible.
  - Documenting fallback instructions (e.g., how to create an external builder) will make future tasks resilient to host limitations.
