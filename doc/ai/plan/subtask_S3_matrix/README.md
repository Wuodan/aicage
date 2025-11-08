# Subtask S3 — Matrix & Helper Scripts

## Objective
Wire the Dockerfile into a reproducible build system using `docker-bake.hcl` and helper scripts that
cover builder bootstrapping, matrix builds, and test execution.

## Deliverables
- `docker-bake.hcl` containing:
  - Global variables (registry, version, platforms, base/tool lists).
  - Target definitions for each base×tool combination under the `matrix` group.
  - Inline tag documentation.
- `scripts/dev/bootstrap.sh` — BuildKit/QEMU setup and `.env` defaults.
- `scripts/build.sh` — Validates inputs, wraps `docker buildx bake`, supports `BASE`, `TOOL`,
  `PLATFORM`, and registry overrides.
- `scripts/test.sh` — Pulls/builds image arguments and runs smoke suites.
- README snippets (placeholder OK until S5) explaining how to run the scripts.

## Flow
1. Define environment variable strategy (`.env` or defaults) for registry, tag, and platforms.
2. Draft `docker-bake.hcl` with locals for tool/base metadata; ensure it stays extendable.
3. Implement scripts with `#!/usr/bin/env bash`, `set -euo pipefail`, two-space indent.
4. Dry-run `docker buildx bake ... --print` to validate matrix expansion.
5. Document usage notes (temporary) either in script headers or README TODO for S5.
6. Update plan checklists and commit `[codex][matrix-build]: add bake + scripts`.

## Checklist
- [ ] Registry/tag/platform variable scheme defined.
- [ ] `docker-bake.hcl` implements matrix + documentation comments.
- [ ] `scripts/dev/bootstrap.sh` provisions builder & QEMU.
- [ ] `scripts/build.sh` wraps Bake with validation.
- [ ] `scripts/test.sh` glues to smoke tests.
- [ ] Dry-run bake succeeds (`--print`).
- [ ] Plan updated; commit `[codex][matrix-build]: add bake + scripts]`.

## Inputs & References
- Dockerfile from S2.
- AGENTS.md build instructions (`docker buildx bake -f docker-bake.hcl matrix ...`).

## Exit Criteria
- All checklist items checked.
- Build/test scripts runnable end-to-end for at least one matrix target.

## Feedback & Learnings
- _Pending._
