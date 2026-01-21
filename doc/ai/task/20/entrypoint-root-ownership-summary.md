# Entrypoint Ownership Issue – Short Reminder

## What I Set Up

- In my container I run with:

  - `AICAGE_USER=root`
  - `AICAGE_UID=1000`
  - `AICAGE_GID=1000`

- I mount my workspace twice:

  - `/workspace`
  - `/mnt/c/development/github/aicage/aicage`

- In `entrypoint.sh` I expect that if the user is `root`, the script will `chown` those paths to root.

- But inside the container, both paths are owned by `1000:1000`, not by root.

## What the Real Problem Is

In `entrypoint.sh`:

```bash
TARGET_USER="${AICAGE_USER:-...}"   # -> root
TARGET_UID="${AICAGE_UID:-...}"     # -> 1000
TARGET_GID="${AICAGE_GID:-...}"     # -> 1000
```

So I end up with:

- `TARGET_USER = root`
- `TARGET_UID = 1000`
- `TARGET_GID = 1000`

Then the script takes the “root branch”:

```bash
if [[ "${TARGET_USER}" == "root" ]]; then
  setup_workspace
fi
```

But `setup_workspace` does:

```bash
chown "${TARGET_UID}:${TARGET_GID}" ...
```

So even in “root mode” it explicitly runs:

```bash
chown 1000:1000 /workspace
chown 1000:1000 /mnt/c/...
```

So nothing is wrong with Docker — the script itself tells it to use `1000:1000`.

## Option A – Simple Fix

Force UID/GID to 0 when user is root.

Right after setting `TARGET_*`:

```bash
TARGET_USER="${AICAGE_USER:-${USER:-aicage}}"
TARGET_UID="${AICAGE_UID:-${UID:-1000}}"
TARGET_GID="${AICAGE_GID:-${GID:-0}}"

if [[ "${TARGET_USER}" == "root" ]]; then
  TARGET_UID=0
  TARGET_GID=0
fi
```

Result:

- If `AICAGE_USER=root` → always chown to `0:0`
- No more accidental “root with uid 1000” situation
