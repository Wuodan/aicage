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

    def test_src_init_files_have_no_methods(self) -> None:
        repo_root = _repo_root()
        src_dir = repo_root / "src"
        violations: list[str] = []
        for path in src_dir.rglob("__init__.py"):
            tree = _parse_tree(path)
            for function_def in _iter_function_defs(tree):
                violations.append(f"{path.relative_to(repo_root)}:{function_def.name}")

        self.assertEqual([], violations, f"Found methods in __init__.py: {violations}")

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
                if not current_package:
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

    def test_public_symbols_are_used_outside_module(self) -> None:
        repo_root = _repo_root()
        src_dir = repo_root / "src"
        modules = _collect_module_info(src_dir)
        usage = _collect_symbol_usage(modules)
        violations: list[str] = []
        for module_name, info in modules.items():
            used_symbols = usage.get(module_name, set())
            for symbol in sorted(info.public_symbols):
                if "*" in used_symbols or symbol in used_symbols:
                    continue
                violations.append(f"{info.path.relative_to(repo_root)}:{symbol}")

        self.assertEqual(
            [],
            violations,
            f"Found public symbols without external usage: {violations}",
        )

    def test_public_modules_are_used_outside_package(self) -> None:
        repo_root = _repo_root()
        src_dir = repo_root / "src"
        modules = _collect_module_info(src_dir)
        usage = _collect_module_usage(modules)
        violations: list[str] = []
        for module_name, info in modules.items():
            if info.path.name in {"__init__.py", "__main__.py"}:
                continue
            if info.path.name.startswith("_"):
                continue
            module_package = _current_package(module_name, info.path)
            if len(module_package) <= 1:
                continue
            importers = usage.get(module_name, set())
            if not _has_outside_package_usage(importers, modules, module_package):
                violations.append(f"{info.path.relative_to(repo_root)}:{module_name}")

        self.assertEqual(
            [],
            violations,
            f"Found public modules without external usage: {violations}",
        )


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


def _iter_function_defs(tree: ast.AST) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


def _iter_imported_modules(tree: ast.AST, current_package: list[str]) -> list[str]:
    imported_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
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


@dataclass(frozen=True)
class _ModuleInfo:
    name: str
    path: Path
    public_symbols: set[str]


def _collect_module_info(src_dir: Path) -> dict[str, _ModuleInfo]:
    modules: dict[str, _ModuleInfo] = {}
    for path in src_dir.rglob("*.py"):
        if path.name == "_version.py":
            continue
        module_name = _module_name_from_path(path, src_dir)
        tree = _parse_tree(path)
        public_symbols = _public_symbols(tree)
        modules[module_name] = _ModuleInfo(
            name=module_name,
            path=path,
            public_symbols=public_symbols,
        )
    return modules


def _public_symbols(tree: ast.AST) -> set[str]:
    symbols: set[str] = set()
    if not isinstance(tree, ast.Module):
        return symbols
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                symbols.add(node.name)
            continue
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    symbols.add(target.id)
            continue
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if not node.target.id.startswith("_"):
                symbols.add(node.target.id)
    return symbols


def _collect_symbol_usage(modules: dict[str, _ModuleInfo]) -> dict[str, set[str]]:
    usage: dict[str, set[str]] = {name: set() for name in modules}
    for module_name, info in modules.items():
        current_package = _current_package(module_name, info.path)
        tree = _parse_tree(info.path)
        alias_map = _collect_import_aliases(tree, current_package, set(modules))
        for imported_module, imported_symbol in _collect_from_imports(tree, current_package):
            if imported_module in usage:
                usage[imported_module].add(imported_symbol)
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                module_alias = node.value.id
                target_module = alias_map.get(module_alias)
                if target_module and target_module in usage:
                    usage[target_module].add(node.attr)
    return usage


def _collect_module_usage(modules: dict[str, _ModuleInfo]) -> dict[str, set[str]]:
    usage: dict[str, set[str]] = {name: set() for name in modules}
    module_names = set(modules)
    for module_name, info in modules.items():
        current_package = _current_package(module_name, info.path)
        tree = _parse_tree(info.path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                _record_import_usage(node, module_name, module_names, usage)
                continue
            if isinstance(node, ast.ImportFrom):
                _record_import_from_usage(
                    node,
                    module_name,
                    current_package,
                    module_names,
                    usage,
                )
    return usage


def _has_outside_package_usage(
    importers: set[str],
    modules: dict[str, _ModuleInfo],
    module_package: list[str],
) -> bool:
    for importer in importers:
        importer_info = modules.get(importer)
        if importer_info is None:
            continue
        importer_package = _current_package(importer, importer_info.path)
        if not _package_starts_with(importer_package, module_package):
            return True
    return False


def _record_import_usage(
    node: ast.Import,
    module_name: str,
    module_names: set[str],
    usage: dict[str, set[str]],
) -> None:
    for alias in node.names:
        _register_module_usage(alias.name, module_name, module_names, usage)


def _record_import_from_usage(
    node: ast.ImportFrom,
    module_name: str,
    current_package: list[str],
    module_names: set[str],
    usage: dict[str, set[str]],
) -> None:
    module_parts = _resolve_relative_module(node.module, node.level, current_package)
    if not module_parts:
        return
    imported_module = ".".join(module_parts)
    _register_module_usage(imported_module, module_name, module_names, usage)
    for alias in node.names:
        if alias.name == "*":
            continue
        _register_module_usage(
            f"{imported_module}.{alias.name}",
            module_name,
            module_names,
            usage,
        )


def _register_module_usage(
    imported_module: str,
    module_name: str,
    module_names: set[str],
    usage: dict[str, set[str]],
) -> None:
    if imported_module in module_names:
        usage[imported_module].add(module_name)




def _collect_import_aliases(
    tree: ast.AST,
    current_package: list[str],
    module_names: set[str],
) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Import):
            continue
        for alias in node.names:
            aliases[alias.asname or alias.name] = alias.name
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        module_parts = _resolve_relative_module(node.module, node.level, current_package)
        if not module_parts:
            continue
        module_name = ".".join(module_parts)
        for alias in node.names:
            if alias.name == "*":
                continue
            full_name = f"{module_name}.{alias.name}"
            if full_name in module_names:
                aliases[alias.asname or alias.name] = full_name
    return aliases


def _collect_from_imports(
    tree: ast.AST,
    current_package: list[str],
) -> list[tuple[str, str]]:
    imports: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        module_parts = _resolve_relative_module(node.module, node.level, current_package)
        if not module_parts:
            continue
        module_name = ".".join(module_parts)
        for alias in node.names:
            if alias.name == "*":
                imports.append((module_name, "*"))
            else:
                imports.append((module_name, alias.name))
    return imports
