# Task 19: Agent claude needs more than 1 mount

2 files and 1 folder:

- /home/stefan/.claude.json
- /home/stefan/.claude.json.backup
- /home/stefan/.claude/

I want to be able to add several paths for `agent_path` in an `agent.yml`.

## Scope

### All `agent.yml` and `agent.schema.json`

The `agent.yml` are originally defined in submodule `aicage-image`. There is also the source of `agent.schema.json`
which is copied from there to other submodules (search yourself).

So with this change adapt (if needed) all `agent.yml` in all submodules to the new format.  
Adapt `agent.schema.json` in submodule `aicage-image`and overwrite other instances of that file.

### entrypoint.sh

Is in submodule `aicage-image-base`.  
It currently handles the one value of `agent_path` with:

- AICAGE_AGENT_CONFIG_MOUNT: The mountpoint from host to container
- AICAGE_AGENT_CONFIG_PATH: the env-variable which is sent from host to container

I'm not really sure what's best to handle several values: As they all are below users HOME, we could:

- either send several AICAGE_AGENT_CONFIG_MOUNT and handle several mount-points as currently the
  `AICAGE_AGENT_CONFIG_PATH`.
- or we could use `/aicage/agent-config` like a partial fake user-home. The host would mount all `agent_path` from there
  relative to normal users-home. Then we don't need env-vars like AICAGE_AGENT_CONFIG_PATH as we can let entrypoint.sh
  just resolve paths relative to users home from what's in `/aicage/agent-config` possibly with help of the `mount`
  command.

### Submodule `aicage`

Must now handle several values of `agent_path`in a matter depending on what approach we do in `entrypoint.sh`.

## Task Workflow

- Don't forget to read AGENTS.md and `doc/python-test-structure-guidelines.md` and respect those rules.
- Always use the existing venv.

You shall follow this order:

1. Read documentation and code to understand the task.
2. Ask me questions if something is not clear to you
3. Present me with an implementation solution - this needs my approval
4. Implement the change autonomously including a loop of running-tests, fixing bugs, running tests
5. Run linters, use `scripts/lint.sh` with active venv
6. Present me the change for review
7. Interactively react to my review feedback
8. Do not commit any changes unless explicitly instructed by the user.
