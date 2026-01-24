# Task 21: Handle CWD subfolder of git-repo root

`aicage` mounts the current working directory to docker containers.

But when the CWD is in a git repository, but not the root of the git-repo, then git cannot really be used in the
container. This also seems to be the case when CWD is the root of a git-submodule.

On Linux I help myself by adding the git-repo root as separate mount to the container. This works because on Linux the
path in the container is the same as on the host.

On Windows the path in the container follows what WSL sees ('/mnt/c/...').

Now it would be nice if `aicage` detect the situation and offered user to:

- mount the git-repo root next to CWD
- mount only the git-repo root and the in the container still start in the same relative path to git-repo-root as the
  CWD has on host.

I do not want both the above options, analyze first what's better.

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
