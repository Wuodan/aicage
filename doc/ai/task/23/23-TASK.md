# Task 23: Remove unused docker images from users PC

`aicage` downloads images to users PC. It also checks and downloads new version of those images.  
But over time this fills users disk with old unused images unless he deletes them manually.

But actually we could do that for him: Currently we check for new images and pull them when needed. After that pull
we could delete the old image by its digest while letting docker decide if the image layer is still used locally.

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
