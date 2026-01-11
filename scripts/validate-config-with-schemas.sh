#!/usr/bin/env bash
set -euo pipefail

SCHEMA_DIR=config/validation

repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

echo "# Validating all config with schemas'" >&2

check-jsonschema --schemafile "${SCHEMA_DIR}"/agent.schema.json config/agent-build/agents/*/agent.yaml
check-jsonschema --schemafile "${SCHEMA_DIR}"/config.schema.json config/config.yaml
check-jsonschema --schemafile "${SCHEMA_DIR}"/images-metadata.schema.json config/images-metadata.yaml
check-jsonschema --schemafile "${SCHEMA_DIR}"/config.schema.json config/config.yaml

echo "Done validating config with schemas" >&2