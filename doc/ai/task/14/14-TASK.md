# Task 14: Integration checks

More and more options are available to users now. I kept testing them and found at least 2 bugs in last few days.

The real problem is not having automated integrations tests, this task shall set them up.

## Integration tests with scenarios simulating user environment and actions

To largely automate my manual tests

Examples:

- docker not installed (ok, a unit-test can cover that)
- npm not installed but used in a version.sh (local agents or local custom agents)
- happy case process for actions user can do:
  - local agents
  - local custom agents
  - extensions
  - custom bases
  - combinations of those with or without npm installed, util-image used or not, etc.

## Task Workflow

Don't forget to read AGENTS.md and always use the existing venv.

You shall follow this order:

1. Read documentation and code to understand the task.
2. Ask me questions if something is not clear to you
3. Present me with an implementation solution - this needs my approval
4. Implement the change autonomously including a loop of running-tests, fixing bugs, running tests
5. Run linters as in the pipeline `.github/workflows/publish.yml` or `scripts/lint.sh` (does the same)
6. Present me the change for review
7. Interactively react to my review feedback
8. Do not commit any changes unless explicitly instructed by the user. Remind him about it when you
   think committing is due.
