# Python Test Structure Guidelines

You are generating **unit and integration tests** for a Python project that follows
**clean architecture**, **small modules**, and **explicit visibility**.

## Core Rules

1. Tests MUST live in packages
   - Always include `__init__.py` in test directories.
   - Do NOT create flat, package-less `tests/` layouts.

2. Mirror the production package structure and module names
   - If code lives in `src/myapp/core/logic.py`
   - Tests go in `tests/core/test_logic.py`
   - If code lives in `src/myapp/core/_logic.py`
   - Tests go in `tests/core/test__logic.py`

3. Tests are architecture-aware
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

## Required Test Coverage For Symbols

- Identify every public and package-private method in `src`.
  - Public: method name does not start with `_` in any module.
  - Package-private: module filename starts with `_` and method name does not start with `_`.
- Includes module-level functions and class methods (instance, class, and static methods).
- Exclude dunder methods like `__init__` and `__call__`.
- Exclude methods defined on Protocol classes (for example, `typing.Protocol`).
- Ignore generated files like `src/aicage/_version.py`.
- Each such method must have at least one matching test method in the correct test module.
  - Test method names must match the source method name.
  - Leading `_` in source names may be dropped in the test name
    (example: `_parse` -> `test_parse` is acceptable).
  - Descriptive suffixes are allowed after an underscore
    (example: `test_parse_handles_empty`).
  - The rule is about structure and naming; it does not replace deeper coverage expectations.

## Required Test Module Presence

- If a `src` module defines any methods covered by the rules above, the corresponding test module must exist.
- Modules without such methods (constants, types, `__init__.py`, `__main__.py`) do not require a test module.

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
