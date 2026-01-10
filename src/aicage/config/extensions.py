from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from aicage.config._yaml import expect_keys, expect_string, load_yaml
from aicage.config.errors import ConfigError
from aicage.paths import CUSTOM_EXTENSION_DEFINITION_FILES, DEFAULT_CUSTOM_EXTENSIONS_DIR


class _HashWriter(Protocol):
    def update(self, data: bytes, /) -> None:
        ...

    def hexdigest(self) -> str:
        ...

_EXTENSION_NAME_KEY: str = "name"
_EXTENSION_DESCRIPTION_KEY: str = "description"
_SCRIPTS_DIRNAME: str = "scripts"
_DOCKERFILE_NAME: str = "Dockerfile"


@dataclass(frozen=True)
class ExtensionMetadata:
    extension_id: str
    name: str
    description: str
    directory: Path
    scripts_dir: Path
    dockerfile_path: Path | None


def load_extensions() -> dict[str, ExtensionMetadata]:
    extensions_dir = DEFAULT_CUSTOM_EXTENSIONS_DIR.expanduser()
    if not extensions_dir.is_dir():
        return {}
    extensions: dict[str, ExtensionMetadata] = {}
    for entry in sorted(extensions_dir.iterdir()):
        if not entry.is_dir():
            continue
        extension_id = entry.name
        definition_path = _find_extension_definition(entry)
        mapping = load_yaml(definition_path)
        expect_keys(
            mapping,
            required={_EXTENSION_NAME_KEY, _EXTENSION_DESCRIPTION_KEY},
            optional=set(),
            context=f"extension metadata at {definition_path}",
        )
        scripts_dir = entry / _SCRIPTS_DIRNAME
        if not scripts_dir.is_dir():
            raise ConfigError(f"Extension '{extension_id}' is missing scripts/ directory.")
        dockerfile_path = entry / _DOCKERFILE_NAME
        extensions[extension_id] = ExtensionMetadata(
            extension_id=extension_id,
            name=expect_string(mapping.get(_EXTENSION_NAME_KEY), _EXTENSION_NAME_KEY),
            description=expect_string(mapping.get(_EXTENSION_DESCRIPTION_KEY), _EXTENSION_DESCRIPTION_KEY),
            directory=entry,
            scripts_dir=scripts_dir,
            dockerfile_path=dockerfile_path if dockerfile_path.is_file() else None,
        )
    return extensions


def extension_hash(extension: ExtensionMetadata) -> str:
    digest = hashlib.sha256()
    definition_path = _find_extension_definition(extension.directory)
    _update_hash(digest, definition_path)
    if extension.dockerfile_path is not None:
        _update_hash(digest, extension.dockerfile_path)
    for script in sorted(extension.scripts_dir.glob("*.sh")):
        if script.is_file():
            _update_hash(digest, script)
    return digest.hexdigest()


def _find_extension_definition(extension_dir: Path) -> Path:
    for filename in CUSTOM_EXTENSION_DEFINITION_FILES:
        candidate = extension_dir / filename
        if candidate.is_file():
            return candidate
    expected = ", ".join(CUSTOM_EXTENSION_DEFINITION_FILES)
    raise ConfigError(f"Extension '{extension_dir.name}' is missing {expected}.")


def _update_hash(digest: _HashWriter, path: Path) -> None:
    digest.update(path.name.encode("utf-8"))
    digest.update(path.read_bytes())
