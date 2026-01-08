# Visibility and __all__

This repository enforces strict visibility rules. Public API must be explicit in names, not inferred by
``__all__`` or by implicit imports. The goal is to keep module boundaries clear, prevent accidental API
expansion, and make reviews and refactors safer.

## Why __all__ is forbidden

- ``__all__`` can hide public/private mistakes by re-exporting private names from a module.
- It makes static checks less reliable because visibility is no longer derived from the identifier name.
- It encourages implicit APIs that are harder to track during refactors.

Instead, public symbols must be named without a leading underscore and be used outside their module.

## Visibility rules

- Module scope: functions, classes, and constants used outside their module are public. Otherwise, they
  must be prefixed with ``_``.
- Package scope: files imported outside their package are public. Internal-only files should be prefixed
  with ``_``.
- Class scope: methods and attributes used outside the class are public. Internal-only members must be
  prefixed with ``_``.

## How enforcement works

- ``tests/aicage/test_visibility.py`` rejects any use of ``__all__``.
- The same test suite flags private modules or symbols referenced outside their scope.
- The public-symbol usage test reports public symbols that are never used outside their defining module.

These checks ensure the public surface stays intentional and small, while private helpers remain private.
