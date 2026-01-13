#!/usr/bin/env bash
set -euo pipefail

SCHEMA_DIR=config/validation

repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

echo "# Validating all config with schemas'" >&2

check-jsonschema --schemafile "${SCHEMA_DIR}"/agent.schema.json config/agent-build/agents/*/agent.yaml
check-jsonschema --schemafile "${SCHEMA_DIR}"/base.schema.json doc/sample/custom/base-images/*/base.yml
check-jsonschema --schemafile "${SCHEMA_DIR}"/extension.schema.json doc/sample/custom/extensions/*/extension.yml
check-jsonschema --schemafile "${SCHEMA_DIR}"/images-metadata.schema.json config/images-metadata.yaml

echo "Done validating config with schemas" >&2
