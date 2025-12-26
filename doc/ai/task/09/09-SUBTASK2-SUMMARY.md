# Subtask 2 Summary: Use Release Images Metadata

## Outcome

Subtask 2 is implemented: image selection and tool configuration now use release images metadata. Registry discovery
and image label inspection were removed in favor of metadata-only lookup and validation.

## Key changes

- Metadata models are public under `src/aicage/registry/images_metadata/models.py`.
- `ConfigContext` and `RunConfig` now carry loaded images metadata for reuse in selection and runtime.
- Image selection uses metadata for valid bases, prompts, and validation in
  `src/aicage/registry/image_selection.py`.
- Tool configuration resolves `tool_path` from metadata in `src/aicage/runtime/tool_config.py`.
- Legacy registry discovery code and tests were removed.
- Tests updated across runtime, registry, and CLI to use images metadata in fixtures.

## Tests run

- `yamllint .`
- `ruff check .`
- `pymarkdown --config .pymarkdown.json scan .`
- `pytest --cov=src --cov-report=term-missing`
