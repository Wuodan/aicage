Last night I let you add the feature to mount additional volumes to the container so everything needed to git-commit as on host (with signing) is available in the images.

And now I think we can simplify this: We do not need to pass the 3 new ENV vars:
- `AICAGE_GITCONFIG_TARGET`
- `AICAGE_GNUPG_TARGET`
- `AICAGE_SSH_TARGET`

as the targets for the symlinks can be fixed:
- .gitconfig to:
  - `$HOME/.gitconfig` and
  - `$HOME/.config/git/config
- .gnupg to `$HOME/.gnupg`
- .ssh to `$HOME/.ssh`

The `scripts/entrypoint.sh` in submodule `aicage-image-base` is currently checking for the ENV vars to be present.  
But it can simply check if the mounts (or target-folders in `/aicage/` for the 3 folders are present and if so symlink them.

This way we can remove those ENV vars and simplify things.

Host-side logic can stay almost the same: check if git/gnupg/ssh folders should be mounted and pass them as volume/mount arguments to docker-run.
But host-side no longer has to pass the ENV vars to docker-run.

I discussed this with ChatGPT and it agreed plus gave me a small markdown file as task description for you. See `doc/ai/task/02/IDEAS-simplify-git-gpg-mounts.md`.

So I want you to:
1. Read the `IDEAS-simplify-git-gpg-mounts.md`, the `entrypoint.sh` in submodule `aicage-image-base` and the python code in this repository (`src/aicage/cli.py` is a good starting point).
2. if anything is unclear: ask me questions
3. present me with a solution/plan - this needs my approval
4. Implement the change
5. Run tests and linters (read AGENTS.md and use the venv at `.venv`)

Ok?
