# AI Agent Playbook

Audience: AI coding agents working in this repo and its submodules. Keep user-facing docs clean and
follow [DEVELOPMENT.md](DEVELOPMENT.md) for workflows.

## Ground rules

- Markdown: wrap near ~120 chars.
- Keep [README.md](README.md) user-only.
- Put build/process notes in [DEVELOPMENT.md](DEVELOPMENT.md).
- For all Python commands, use a virtualenv:  
  `python -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt`.
- Keep code and docs free of conversational feedback to humans; only ship product-ready content.
- Disabling linters via comments (e.g., `# noqa`) is a last resort; analyze and fix first, and only
  add suppressions with explicit approval.

## Repo structure

- [README.md](README.md) (users)
- [DEVELOPMENT.md](DEVELOPMENT.md) (advanced users)
- [Why cage agents?](README.md#why-cage-agents) (rationale).
- Submodules:
  - `aicage-image-base/` builds base OS layers
  - `aicage-image/` builds final agent images

## Linting and tests

- Lint: `yamllint .`, `ruff check .`, `pymarkdown --config .pymarkdown.json scan .`
- Tests: `pytest --cov=src --cov-report=term-missing`
