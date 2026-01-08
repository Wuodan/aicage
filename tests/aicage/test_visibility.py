import ast
from dataclasses import dataclass
from pathlib import Path
from unittest import TestCase


class VisibilityRulesTests(TestCase):
    def test_src_has_no_all(self) -> None:
        repo_root = _repo_root()
        src_dir = repo_root / "src"
        violations: list[Path] = []
        for path in src_dir.rglob("*.py"):
            if path.name == "_version.py":
                # Generated file from setuptools-scm; allow __all__ in version metadata.
                continue
            if "__all__" in path.read_text(encoding="utf-8"):
                violations.append(path.relative_to(repo_root))

        self.assertEqual([], violations, f"Found __all__ usage: {violations}")

    def test_src_init_files_do_not_import_private_modules(self) -> None:
        repo_root = _repo_root()
        src_dir = repo_root / "src"
        violations: list[str] = []
        for path in src_dir.rglob("__init__.py"):
            module_name = _module_name_from_path(path, src_dir)
            current_package = _current_package(module_name, path)
            tree = _parse_tree(path)
            for imported in _iter_imported_modules(tree, current_package):
                if imported == "aicage._version" and module_name == "aicage":
                    continue
                if _has_private_segment(imported):
                    violations.append(f"{path.relative_to(repo_root)}:{imported}")

        self.assertEqual([], violations, f"Found private imports in __init__.py: {violations}")

    def test_src_private_modules_not_imported_outside_package(self) -> None:
        repo_root = _repo_root()
        src_dir = repo_root / "src"
        violations: list[str] = []
        for path in src_dir.rglob("*.py"):
            if path.name == "__init__.py":
                continue
            module_name = _module_name_from_path(path, src_dir)
            current_package = _current_package(module_name, path)
            tree = _parse_tree(path)
            for imported in _iter_imported_modules(tree, current_package):
                private_parent = _private_parent_package(imported)
                if private_parent is None:
                    continue
                if private_parent == [] and current_package != []:
                    violations.append(f"{path.relative_to(repo_root)}:{imported}")
                    continue
                if current_package == []:
                    continue
                if not _package_starts_with(current_package, private_parent):
                    violations.append(f"{path.relative_to(repo_root)}:{imported}")

        self.assertEqual([], violations, f"Found private module imports across packages: {violations}")

    def test_src_has_no_runtime_imports_or_exec(self) -> None:
        repo_root = _repo_root()
        src_dir = repo_root / "src"
        violations: list[str] = []
        for path in src_dir.rglob("*.py"):
            tree = _parse_tree(path)
            violations.extend(_runtime_import_violations(tree, path.relative_to(repo_root)))

        self.assertEqual([], violations, f"Found runtime imports or exec/eval usage: {violations}")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _module_name_from_path(path: Path, src_dir: Path) -> str:
    rel_path = path.relative_to(src_dir)
    parts = list(rel_path.parts)
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1][:-3]
    return ".".join(parts)


def _current_package(module_name: str, path: Path) -> list[str]:
    if not module_name:
        return []
    parts = module_name.split(".")
    if path.name == "__init__.py":
        return parts
    return parts[:-1]


def _parse_tree(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"))


def _iter_imported_modules(tree: ast.AST, current_package: list[str]) -> list[str]:
    imported_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "__future__":
                    continue
                imported_modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                if node.module == "__future__":
                    continue
                imported_modules.append(node.module)
                continue
            resolved_base = _resolve_relative_module(node.module, node.level, current_package)
            if not resolved_base:
                continue
            if node.module:
                imported_modules.append(".".join(resolved_base))
                continue
            for alias in node.names:
                imported_modules.append(".".join(resolved_base + alias.name.split(".")))
    return imported_modules


def _resolve_relative_module(
    module: str | None,
    level: int,
    current_package: list[str],
) -> list[str] | None:
    if level == 0:
        if not module:
            return None
        return module.split(".")
    if level > len(current_package) + 1:
        return None
    prefix = current_package[: len(current_package) - (level - 1)]
    if module:
        return prefix + module.split(".")
    return prefix


def _has_private_segment(module_name: str) -> bool:
    return any(part.startswith("_") for part in module_name.split("."))


def _private_parent_package(module_name: str) -> list[str] | None:
    parts = module_name.split(".")
    for index, part in enumerate(parts):
        if part.startswith("_"):
            if index == 0:
                return []
            return parts[:index]
    return None


def _package_starts_with(package: list[str], prefix: list[str]) -> bool:
    if len(prefix) > len(package):
        return False
    return package[: len(prefix)] == prefix


def _runtime_import_violations(tree: ast.AST, path: Path) -> list[str]:
    aliases = _collect_runtime_import_aliases(tree)
    violations: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function_name = _call_name(node, aliases)
        if function_name:
            violations.append(f"{path}:{node.lineno}:{function_name}")
    return violations


@dataclass
class _RuntimeImportAliases:
    importlib: set[str]
    import_module: set[str]
    exec_names: set[str]
    eval_names: set[str]


def _collect_runtime_import_aliases(tree: ast.AST) -> _RuntimeImportAliases:
    importlib_aliases: set[str] = set()
    import_module_aliases: set[str] = set()
    exec_aliases: set[str] = set()
    eval_aliases: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "importlib":
                    importlib_aliases.add(alias.asname or alias.name)
            continue
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.module == "importlib":
            for alias in node.names:
                if alias.name == "import_module":
                    import_module_aliases.add(alias.asname or alias.name)
        if node.module == "builtins":
            for alias in node.names:
                if alias.name == "exec":
                    exec_aliases.add(alias.asname or alias.name)
                if alias.name == "eval":
                    eval_aliases.add(alias.asname or alias.name)
    return _RuntimeImportAliases(
        importlib=importlib_aliases,
        import_module=import_module_aliases,
        exec_names=exec_aliases,
        eval_names=eval_aliases,
    )


def _call_name(node: ast.Call, aliases: _RuntimeImportAliases) -> str | None:
    function_name: str | None = None
    if isinstance(node.func, ast.Name):
        name = node.func.id
        if name in {"__import__", "exec", "eval"}:
            function_name = name
        elif name in aliases.exec_names:
            function_name = "exec"
        elif name in aliases.eval_names:
            function_name = "eval"
        elif name in aliases.import_module:
            function_name = "importlib.import_module"
    elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
        if node.func.value.id in aliases.importlib and node.func.attr == "import_module":
            function_name = "importlib.import_module"
    return function_name
