# Python Test Structure Guidelines

You are generating **unit and integration tests** for a Python project that follows **clean architecture**, **small modules**, and **explicit visibility**.

## Core Rules

1. **Tests MUST live in packages**
   - Always include `__init__.py` in test directories.
   - Do NOT create flat, package-less `tests/` layouts.

2. **Mirror the production package structure**
   - If code lives in `src/myapp/core/logic.py`
   - Tests go in `tests/core/test_logic.py`

3. **Tests are architecture-aware**
   - Respect module boundaries.
   - Do not mix unrelated layers in the same test file.

## Required Layout

Use the following layout.

### Mirrored structure

```text
src/myapp/
├─ core/
│  └─ logic.py
└─ infra/
   └─ db.py

tests/
├─ core/
│  ├─ __init__.py
│  └─ test_logic.py
└─ infra/
   ├─ __init__.py
   └─ test_db.py
```

## Imports & Visibility

- Explicit imports only (no implicit test discovery tricks)
- Shared helpers MUST live in test packages, never as loose files
- Testing private functions (`_internal_fn`) is allowed **only if they contain real logic**

## Pytest Expectations

- Pytest discovery must work **without modifying `sys.path`**
- No reliance on cwd-relative imports
- Tests must be runnable via:

```bash
pytest
```

## Anti-Patterns (DO NOT DO)

- Flat `tests/*.py` without `__init__.py`
- Mixing unit and integration tests
- Shared helpers outside a package
- Reaching across layers without intent

## Goal

Tests should reflect **architectural intent**, not just execute code.

Optimize for:
- refactor safety
- clarity
- long-term maintainability

Not for:
- minimal boilerplate
- tutorial-style layouts
