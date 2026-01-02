# Subtask 05 summary

## Context

- Subtask id and title: 05 - Local build pipeline for non-redistributable agents.
- Related subtasks touched or impacted: 04, 06.

## Changes

- Key decisions (why): Non-redistributable agents build to local `aicage:<agent>-<base>` tags; packaged build
  context lives under `config/agent-build/` with only non-redistributable agents included; base image repository is
  configurable via `image_base_repository`; local builds always use `--no-cache` to avoid stale agent installs and
  each build/pull writes to a dedicated log file.
- User-visible behavior changes: Non-redistributable agents now build locally before run, using base-image updates to
  decide rebuilds; build and base-image pull logs are written under `~/.aicage/logs/build/` with per-run filenames.
- Internal behavior changes: Added local build metadata under `~/.aicage/state/local-build/`, integrated version checks
  for non-redistributable agents, and added base-image digest checks using the existing registry query flow.
- Files and modules with major changes:
  - src/aicage/cli.py
  - src/aicage/config/runtime_config.py
  - src/aicage/registry/_local_build.py
  - src/aicage/registry/image_selection.py
  - src/aicage/registry/_remote_query.py
  - src/aicage/registry/image_pull.py
  - config/config.yaml
  - doc/validation/config.schema.json
  - CHANGELOG.md
  - doc/update-processes.md
  - config/agent-build/Dockerfile
  - config/agent-build/agents/claude/agent.yaml
  - config/agent-build/agents/claude/install.sh
  - config/agent-build/agents/claude/version.sh
  - config/agent-build/agents/droid/agent.yaml
  - config/agent-build/agents/droid/install.sh
  - config/agent-build/agents/droid/version.sh

## Testing and validation

- Tests run:
  - `yamllint .`
  - `ruff check .`
  - `pymarkdown --config .pymarkdown.json scan .`
  - `pytest --cov=src --cov-report=term-missing`
- Gaps or skipped tests and why: None.

## Follow-ups

- Deferred items (explicitly list): None.
- Known risks or open questions: Build logic assumes local Docker availability; remote digest lookup for base images
  skips rebuilds if the registry query fails.
- Suggested next steps: Validate local build with a non-redistributable agent against a fresh base-image update.

## Notes

- Lessons learned: Keep build artifacts packaged under config to avoid submodule dependency at runtime; only commit or
  write the subtask summary when the user explicitly instructs to do so.
- Review feedback to carry forward: Maintain local image naming without registry prefixes.
