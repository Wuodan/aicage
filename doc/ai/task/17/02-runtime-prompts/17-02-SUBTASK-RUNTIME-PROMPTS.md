# Subtask 17-02: Adapt runtime prompting and selection to ConfigContext data

## Goal

Stop reading agent/base fields from `images_metadata` during user interaction and selection.
Use `ConfigContext.agents` and `ConfigContext.bases` instead, with base filtering applied once.

## Current state

- Runtime prompts and selection use `images_metadata` to access agents, bases, and base descriptions.
- Base filtering uses `base_exclude` and `base_distro_exclude` inside `images_metadata` flows.

## Proposed changes

- Update prompting and selection logic to read from `ConfigContext.agents` and `ConfigContext.bases`.
- Filter available bases per agent on the fly using `base_exclude` and `base_distro_exclude` stored
  on `AgentMetadata`.
- Keep `RunConfig.selection` as the source of truth for chosen base after prompt/selection.

## Impact

- Medium: touches user interaction and selection logic.
- Ensures only one evaluation of exclusion rules.

## Acceptance criteria

- Prompting and selection only access `ConfigContext.agents` and `ConfigContext.bases`.
- `images_metadata` is no longer used in runtime prompt/selection paths.
- Tests updated and follow test-structure guidelines.

## Tests

- Unit tests under `tests/aicage/runtime` and `tests/aicage/registry/image_selection`.

## Subtask Guidelines and Workflow

Don't forget to read `AGENTS.md` and `doc/python-test-structure-guidelines.md`; always use the existing venv.

You shall follow this order:

1. Read documentation and code to understand the task.
2. Ask me questions if something is not clear to you
3. Present me with an implementation solution - this needs my approval
4. Implement the change autonomously including a loop of running-tests, fixing bugs, running tests
5. Run linters with `scripts/lint.sh`
6. Present me the change for review
7. Interactively react to my review feedback
8. Do not commit any changes unless explicitly instructed by the user.
