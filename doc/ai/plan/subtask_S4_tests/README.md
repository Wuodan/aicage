# Subtask S4 — Smoke Tests

## Objective
Provide smoke-test coverage for every tool so that `scripts/test.sh` can verify container boot,
agent CLI availability, and core OS packages on both amd64 and arm64 images.

## Deliverables
- `tests/smoke/` directory with:
  - Shared helpers (`common.bash`) for assertions and env handling.
  - One Bats file per tool (`cline.bats`, `codex.bats`, `factory_ai_droid.bats`).
- Tests cover:
  - `test_boots_container`
  - `test_agent_binary_present`
  - `test_required_packages`
- Documentation update describing how to run tests (full details may wait for S5).

## Flow
1. Review outputs from S2/S3 to learn container entrypoints and binary paths.
2. Create helper script for repeated logic (starting container, exec, cleanup).
3. Author individual Bats suites aligned with AGENTS.md naming guidance.
4. Execute tests locally via `scripts/test.sh <image>` (even if mocked/dry-run).
5. Update plan checklist and add summary to Feedback.
6. Commit `[codex][tests]: add smoke suites]`.

## Checklist
- [ ] Helper script created with reusable assertions.
- [ ] Per-tool Bats suites implement required tests.
- [ ] Tests integrated with `scripts/test.sh`.
- [ ] Sample test run recorded (log or note).
- [ ] Plan updated; commit `[codex][tests]: add smoke suites]`.

## Inputs & References
- Outputs from S2 (install locations) and S3 (image tags).
- `tests/smoke/*.bats` guidance in AGENTS.md.

## Exit Criteria
- All checklist items complete.
- Tests pass (or documented limitations) for at least one matrix target.

## Feedback & Learnings
- _Pending._
