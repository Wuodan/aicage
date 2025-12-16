## Simplify git / signing mounts inside the container

**Goal:** remove path/env-var bloat in `entrypoint.sh`.  
Host paths are resolved *before* `docker run`.  
Inside the container we always use **fixed, standard locations**.

### Rules

1. **Do NOT pass target paths via env vars**
   - No `AICAGE_GITCONFIG_TARGET`
   - No `AICAGE_GNUPG_TARGET`
   - No `AICAGE_SSH_TARGET`

2. **Assume standard container targets**
   - Git global config:
     - `$HOME/.gitconfig`
     - `$HOME/.config/git/config` (**symlink to the same file**)
   - GPG:
     - `$HOME/.gnupg`
   - SSH:
     - `$HOME/.ssh`

3. **Symlink strategy (important)**
   - If `/aicage/host/gitconfig` exists:
     - symlink it to **both**
       - `$HOME/.gitconfig`
       - `$HOME/.config/git/config`
   - This covers legacy + XDG Git behavior without env vars.

4. **Why**
   - Host locations are dynamic → resolved by launcher
   - Container locations are predictable
   - Git/GPG auto-discover correctly
   - Works across Debian/Ubuntu/Fedora/Alpine

### Expected behavior
After this change:
- `git config --global --show-origin` works in-container
- GPG signing works with mounted `$HOME/.gnupg`
- SSH signing works with mounted `$HOME/.ssh`
- Entry point logic is smaller and clearer
