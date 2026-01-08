# Task 14 summary

## Context

- Task id and title: 14 - Integration checks.
- Related tasks touched or impacted: 15 (base-image digest validation idea tracked separately).

## Changes

- Key decisions (why): Use real Docker/network flows in integration tests; isolate HOME to avoid touching developer state;
  restructure tests by build mode for scalability; rename CLI flag to avoid collision with docker `--entrypoint`.
- User-visible behavior changes:
  - CLI flag `--entrypoint` renamed to `--aicage-entrypoint`.
  - Custom agent directory moved to `~/.aicage/custom/agents/`.
- Internal behavior changes:
  - Integration tests now run in isolated packages under `tests/aicage/integration/` by build mode and use PTY runner.
  - Integration workflow discovers tests and runs each node id in its own job.
  - Remote digest lookup now accepts lowercase `docker-content-digest` header.
- Files and modules with major changes:
  - `tests/aicage/integration/_helpers.py`
  - `tests/aicage/integration/remote_builtin/test_run.py`
  - `tests/aicage/integration/remote_builtin/test_pull_newer.py`
  - `tests/aicage/integration/local_builtin/test_rebuild_agent_version.py`
  - `tests/aicage/integration/local_builtin/test_rebuild_base_digest.py`
  - `tests/aicage/integration/local_custom/test_build_and_version.py`
  - `tests/aicage/integration/local_custom/test_rebuild_agent_version.py`
  - `tests/aicage/integration/local_custom/test_rebuild_base_digest.py`
  - `doc/integration-tests.md`
  - `.github/workflows/integration-test.yml`
  - `.github/workflows/publish.yml`
  - `src/aicage/cli/_parse.py`
  - `tests/aicage/cli/test_cli_parse.py`
  - `README.md`
  - `src/aicage/registry/_remote_query.py`

## Testing and validation

- Tests run: `ruff check .`; targeted integration tests run by the user.
- Gaps or skipped tests and why: Full integration suite not re-run in this summary.

## Follow-ups

- Deferred items (explicitly list): None.
- Known risks or open questions: `doc/integration-tests.md` expected-failure note may need revisiting after digest
  header fix.
- Suggested next steps: Re-evaluate integration test expectations and update docs if behavior has changed.

## Notes

- Lessons learned: Registry headers are case-insensitive; digest lookups must normalize header keys.
- Review feedback to carry forward: Keep integration tests isolated from user state and prefer real workflows over stubs.
