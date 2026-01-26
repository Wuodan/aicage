# Subtask 17-03: Adapt image pull/check/build to ConfigContext data

## Goal

Remove remaining `images_metadata` usage in image pulling, checking, and building paths.
Use `ConfigContext.agents`, `ConfigContext.bases`, and `RunConfig.selection` instead.

## Current state

- Registry and local build logic still read `images_metadata` and `custom_bases` directly.
- Base filtering may be applied more than once.

## Proposed changes

- Update image check/pull/build paths to use:
  - `ConfigContext.agents` for agent metadata
  - `ConfigContext.bases` for base metadata
  - `RunConfig.selection` for already-filtered base choices
- Remove any secondary filtering of `base_exclude` and `base_distro_exclude`.

## Impact

- Medium to high: touches runtime-critical paths and tests.

## Acceptance criteria

- No remaining `images_metadata` usage in pull/check/build code paths.
- `RunConfig.selection` is trusted for base choice; exclusion rules are not re-applied.
- Tests updated and follow test-structure guidelines.

## Tests

- Unit tests in `tests/aicage/registry` and any impacted integrations.

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
