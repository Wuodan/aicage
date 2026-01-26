# Subtask 08.1: Custom base discovery and selection

## Goal

Introduce custom base discovery and selection integration without changing build/update logic.

## Rationale

Separating discovery/selection from build/update keeps the behavior changes small and makes review
of override rules and validation easier.

## Dependencies

- Task 12 overview: doc/ai/task/12/12-TASK.md
- Subtask 08: doc/ai/task/12/08/08-SUBTASK.md
- Agent workflow rules: AGENTS.md

## Scope

- Add schema validation for custom base configs.
- Discover custom bases under `~/.aicage/custom/base-images/<BASE>/`.
- Accept `base.yaml` and `base.yml`.
- Require a `Dockerfile` in each custom base folder.
- Merge custom bases into selection and prompt flow for all agents.
- Custom bases override built-in bases by name.
- Custom base descriptions come from user config; no grouping or suffix in prompts.

## Out of scope

- Any image build logic.
- Digest-based update logic.
- Integration tests (unit tests only).

## Expected outputs

- Custom base configs are validated and discoverable.
- Base selection includes custom bases for all agents.
- Conflicts are resolved by custom base override.

## Sequencing

Run before Subtask 08.2.

## Notes

Follow the Task/SubTask Workflow in doc/ai/task/12/12-TASK.md. See the `## Task/SubTask Workflow`
section. Do not write a subtask summary unless explicitly requested.
