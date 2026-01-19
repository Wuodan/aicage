# Task 18: Gradually replace `config/images-metadata.yaml` with `config/base-build/bases/*/base.yaml`

Currently, the paths are mostly for Linux and we should support Windows as much as can easily be done.

When I currently run `aicage codex` and select base=ubuntu, then I get errors from docker:
`docker: Error response from daemon: invalid mode: \development\github\aicage\aicage`


Running `aicage --dry-run codex` to see actual docker-run command prints this (formatted with PS1 line-breaks here):
```
docker run --rm -it `
	-e AICAGE_USER=stefa `
	-e 'AICAGE_WORKSPACE=C:\development\github\aicage\aicage' `
	-e 'AICAGE_AGENT_CONFIG_PATH=~/.codex' `
	-v 'C:\development\github\aicage\aicage:/workspace' `
	-v 'C:\development\github\aicage\aicage:C:\development\github\aicage\aicage' `
	-v 'C:\Users\stefa\.codex:\aicage\agent-config' `
	-v 'C:\Users\stefa\.gitconfig:\aicage\host\gitconfig' `
	ghcr.io/aicage/aicage:codex-ubuntu
```

Several arguments to docker-run cause problems for sure:
1. `-e 'AICAGE_WORKSPACE=C:\development\github\aicage\aicage'`
2. `-v 'C:\development\github\aicage\aicage:C:\development\github\aicage\aicage'`
3. `-v 'C:\Users\stefa\.codex:\aicage\agent-config'`
4. `-v 'C:\Users\stefa\.gitconfig:\aicage\host\gitconfig'`

The 1. sets `AICAGE_WORKSPACE` which is used by the entrypoint script `aicage-image-base/scripts/entrypoint.sh` in the
container. Here, when on Windows, we should not send that ENV var to the container or send the default `/workspace`.

The 2. is a second mount for the current-working folder. It's a backup, so on Windows we should simply not set that
backup mount.

I have not yet looked deeply into 3. and 4. but somehow those fixed paths `\aicage\agent-config` and
`\aicage\host\gitconfig` get converted to windows path style.

Also searching for `"/aicage` in `src` and `tests` shows hardcoded paths deep in the code. But they should all be
defined in `src/aicage/paths.py` and referenced in the rest of the code.

A good starting point for both changes is `src/aicage/docker/run.py` where both 1. and 2. are sent to docker-run in
method `_assemble_docker_run()`.

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