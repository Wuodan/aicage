# Task 16: Centralize docker access

Right now docker is used in several places in the `aicage` Python code, both as system `docker` command and also by
the Python `docker` library.

This has gotten a bit out of hand as those interactions with Docker are spread throughout the project.

As Docker is the main external software that `aicage` interacts with, I'd rather have those
interactions with Docker centralized in a package structure (one package or even a package with
several sub-packages).

I want you to:

1. Analyze the situation and tell me your opinion:
   - Am I wrong, and it is best practice to keep such access spread out as we mostly interact with only one external
     software?
   - If you agree with me: What is a good place/structure for such access? (open discussion between you and me)
2. If needed: Ask me questions about things unclear or vague to you.
3. Propose an implementation plan for me to review. This plan needs my approval. If you think the
   task is large, feel free to suggest splitting it into subtasks, eahc following the further steps
   below
4. Implement the changes self-sufficient. This includes tests and integration-tests (respect
   `doc/python-test-structure-guidelines.md`).
5. Run `script/lint.sh` for linting and the tests, excluding integration-tests (large logs, I run them manually myself).
6. Without committing, ask me to review the changes. This is interactive, I often have a few
   change-request, then tell you to commit before I feed you more change requests. These in-between
   commits help me see further changes separately while cleaning the diff from time to time.

> Do NOT commit by yourself, I will tell you when to commit - always. And when I tell you to commmit it is always a one
> time request not an approval to commit autonomously for the rest of the session.

## Side-task: Open question - Remote image (digest) lookup

While the lookups for remote images or rather their digests are technically not using docker, they are closely related.
So close, that the only reason we are not using Docker directly for this is that Docker itself does not provide that
functionality to us.

So I want you look at the situation for this too. If you agree wholesome, then add this to the
main task 16 workflow, possibly as side-task or subtask.

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
8. Do not commit any changes unless explicitly instructed by the user. Remind him about it when you think committing
   is due.
