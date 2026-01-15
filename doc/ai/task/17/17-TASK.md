# Task 17: Gradually replace `config/images-metadata.yaml` with `config/base-build/bases/*/base.yaml`

I just added `config/base-build/bases/` (and methods to sync it on release).  

With this we now have all base.yml locally, not just the custom ones.

With all bases and all agents we now have all information contained on `images-metadata.yaml` and could live without.
But this is no small task so let's do it gradually.

## General Rules and Guidelines

- Read `AGENTS.md` and `doc/python-test-structure-guidelines.md` and respect those rules
- Data from YAML files is loaded once only and stored in ConfigContext. I do not want access to those files later in the
  process.

## Subtasks

### Subtask 0: Review task instructions, prepare subtask 1-3

First analyze these task instructions and related documents, do a high-level code analysis to grasp the magnitude.
Then ask me questions - together we can improve these task instructions.

I think this is too much to do cleanly in one session.  
So I want you to create subtask documents in subfolders of `doc/ai/task/17`.

## Subtask 1: Load all bases and all agents into dataclass `ConfigContext`

`ConfigContext` (`src/aicage/config/context.py`) now only holds `custom_bases` separately, all other bases and agents
are in `images_metadata`.

As first step I want you to:
- Add new fields to dataclass `BaseMetadata` (similar to fields in `AgentMetadata`):
  - `build_local: bool`: needed for later decision if we need to build or pull the base-image
    - true for custom-bases
    - false for built-in bases unless explicitly set to true in the `base.yml` - I might want to add that to builtin
      base-images (submodule `aicage-image-base` in the future).
    - Also add that field to `config/validation/base.schema.json` with a default
  - `local_definition_dir: Path | None = None`: When `build_local` is true, the later process looks here.
    Important: Decisions are made based on `build_local`, not on `local_definition_dir` being None or not (you did that
    with custom-agents, and it took a while until I noticed and refactoring took time)
- In `ConfigContext`:
  - rename `custom_bases` to `bases` and adapt named methods and variables (also in tests). Do not
    rename in parts of the code where only `custom_bases` are handled.
  - add new field `agents: dict[str, AgentMetadata]` where all agents (both builtin and custom) are stored. custom
    agents override builtin (by name).
  - add new field `bases: dict[str, BaseMetadata]` where all bases (both builtin and custom) are stored. custom
    bases override builtin (by name).

Implementation strategy:
- Next to the changes to dataclass, we need to load all agents and bases from YAML files. This logic already exists in
  packages `custom_agent` and `custom_base` and just needs to be tweaked and renamed to now load all objects (builtin
  and custom).
- in `load_run_config()` in `src/aicage/config/runtime_config.py`:
  - load all bases not just custom ones.
  - load all agents
  - path all agents and bases to package `images_metadata` with `load_images_metadata(bases, agents)`
- package `images_metadata` will be replaced when we no longer need images-metadata. But for now it must be adapted to
  no longer loading agents itself and to filter out builtin bases and builtin agents in its process.
- Update affected unit-tests (respect `python-test-structure-guidelines.md`), also rename variables and methods.

This should have little or no effect on code for the later process as those new fields are not yet used.  
But now we have the information of `images_metadata` duplicated in `ConfigContext` and can gradually merge the process.

## Subtask 2: Adapt user-interaction which creates RunTimeConfig

Start with user-prompting/-interactions and replace usage of `images_metadata`.

This involves
- filtering available bases per agent on-the-fly (based on agents fields `base_exclude` and `base_distro_exclude`)
- reading fields for agents/bases from `ConfigContext.agents` and `ConfigContext.bases` and no longer from
  `images_metadata`
- update tests, also rename variables and methods.

## Subtask 3: Adapt image pulling/checking/building process

This is the last part where data can be read `images_metadata`. Change the logic so:
- `ConfigContext.agents` and `ConfigContext.bases` are used, not `ConfigContext.images_metadata`
- Trust the previous filtering of bases and `RunConfig.selection`. I do not want a second evaluation of `base_exclude`
  and `base_distro_exclude`.
- update tests, also rename variables and methods.

A good check for completeness is that
`ConfigContext.images_metadata` and then package `images_metadata` is no longer in use and both can be deleted along
with:
- config/images-metadata.yaml
- config/validation/images-metadata.schema.json

## Subtask 4: Update documentation

- Review documentation, update it when needed
- Write summary Markdown for Task 17

## Subtask 1-4: Workflow

- Don't forget to read AGENTS.md and `doc/python-test-structure-guidelines.md` and respect those rules.
- Always use the existing venv.

You shall follow this order:

1. Read documentation and code to understand the task.
2. Ask me questions if something is not clear to you
3. Present me with an implementation solution - this needs my approval
4. Implement the change autonomously including a loop of running-tests, fixing bugs, running tests
5. Run linters as in the pipeline `.github/workflows/publish.yml` or `scripts/lint.sh` (does the same)
6. Present me the change for review
7. Interactively react to my review feedback
8. Do not commit any changes unless explicitly instructed by the user.
