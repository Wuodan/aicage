# Subtask 17-01: Load all bases and agents into ConfigContext

## Goal

Load all base and agent metadata (builtin + custom) into `ConfigContext`, while keeping
`images_metadata` available for the rest of the code during the transition.

## Current state

- `ConfigContext` holds `images_metadata` plus `custom_bases`.
- `images_metadata` is loaded from `config/images-metadata.yaml` and then merged with custom
  bases/agents via `discover_bases` and `discover_agents`.
- Custom base and agent loaders only read the custom dirs and rely on `images_metadata` for base
  filtering.

## Proposed changes

- `BaseMetadata` gains:
  - `build_local: bool` (default false in schema; true for custom bases; optional in builtin base YAML)
  - `local_definition_dir: Path | None = None`
- `config/validation/base.schema.json` adds `build_local` with a default.
- `ConfigContext` adds:
  - `agents: dict[str, AgentMetadata]` (builtin + custom; custom overrides by name)
  - `bases: dict[str, BaseMetadata]` (builtin + custom; custom overrides by name)
  - Rename `custom_bases` to `bases` (only where it now holds all bases, not where only customs
    are meant)
- Load all bases and agents from YAML:
  - Add loader(s) that read builtin `config/base-build/bases/*/base.yaml` plus custom base
    definitions, setting `build_local` accordingly and `local_definition_dir` for custom bases.
  - Add loader(s) that read builtin agent definitions from `images_metadata` plus custom agents,
    then merge into `ConfigContext.agents` with custom override.
  - Update `load_run_config()` to populate `context.agents` and `context.bases`, and to call
    `load_images_metadata(bases, agents)` so `images_metadata` can be derived from these sources.
- Adapt `images_metadata` package to accept bases/agents inputs and to skip re-loading agents or
  bases itself (no direct file IO outside the config loaders).

## Impact

- Medium: new data flow is introduced, but behavior should remain the same.
- Data duplication in `ConfigContext` is expected for now.

## Acceptance criteria

- `ConfigContext` contains all agents and bases; custom entries override builtin ones.
- `BaseMetadata` includes `build_local` and `local_definition_dir` with correct defaults.
- `load_run_config()` loads all bases and agents and derives `images_metadata` from them.
- `images_metadata` package no longer loads agents/bases directly from disk.
- Tests updated to reflect new data flow and naming rules.

## Tests

- Unit tests in `tests/aicage/config` and any impacted areas.

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
