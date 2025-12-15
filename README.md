# aicage

Run your favorite AI coding agents in Docker with a host-matching user and your local config mounted
automatically.

## Why cage agents?

Agents need deep access (read code, run shells, install deps).
Their built-in safety checks are naturally limited.

Running agents in containers gives a hard boundary - while the experience stays the same.
See [Why cage agents? (detailed)](#why-cage-agents-detailed) for the full rationale.

## Quickstart

- Prerequisites: Docker, Python 3.10+, and `pipx` (or `pip` if you prefer).
- Install: `pipx install aicage` (or `pip install aicage`).
- Use from a project directory:

  ```bash
  aicage claude
  aicage cline
  aicage codex
  aicage droid
  ```

## Base images

The first run asks which base image to use; pick Ubuntu or whatever matches your Linux distro.

| Base   | Notes                                          |
|--------|------------------------------------------------|
| ubuntu | Good default for most users.                   |
| debian | Stable Debian base.                            |
| fedora | Fedora users can choose this.                  |
| alpine | Minimal footprint; more packages may be needed.|
| node   | Official Node image (Ubuntu-based).            |
| act    | Default runner image from `act`.               |

## Agents

- claude — Anthropic Claude CLI · [anthropic.com](https://www.anthropic.com)
- cline — Cline VS Code-style agent · [github.com/cline/cline](https://github.com/cline/cline)
- codex — OpenAI-style agent · [openai.com](https://openai.com)
- droid — Dev-Droid assistant · [github.com/ckaznocha/devdroid](https://github.com/ckaznocha/devdroid)

Your existing CLI config for each tool is mounted inside the container so you can keep using your
preferences and credentials.

## aicage options

- `--dry-run` prints the composed `docker run` command without executing it.

## More info

More details are in [DEVELOPMENT.md](DEVELOPMENT.md).

## Why cage agents? (detailed)

AI coding agents read your code, run shells, install packages, and edit files. That power is useful,
but granting it directly on the host expands your risk surface.

Where built-in safety is limited:

- Allow/deny lists only cover known patterns; unexpected commands or attack paths can slip through.
- Some tools work fully only after relaxing their own safety modes, broadening what they can touch.
- “Read-only project” features are software rules. Other projects and files still sit alongside them
  on the same host.

How aicage mitigates this:

- Containers create a hard boundary: the agent can access only what you explicitly mount. Day-to-day
  use stays familiar—just with the host kept out of reach.
