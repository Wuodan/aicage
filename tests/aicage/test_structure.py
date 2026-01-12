import ast
from pathlib import Path
from unittest import TestCase


class TestStructureRulesTests(TestCase):
    def test_public_and_package_private_methods_have_tests(self) -> None:
        repo_root = _repo_root()
        src_dir = repo_root / "src"
        tests_dir = repo_root / "tests"
        violations: list[str] = []
        for path in src_dir.rglob("*.py"):
            if _should_skip_src_module(path):
                continue
            required_methods = _required_methods_in_module(path)
            if not required_methods:
                continue
            test_module_path = _test_module_path_for_src(path, src_dir, tests_dir)
            if not test_module_path.exists():
                violations.append(f"{path.relative_to(repo_root)}:missing {test_module_path.relative_to(repo_root)}")
                continue
            test_methods = _test_method_names(test_module_path)
            missing = sorted(
                name
                for name in required_methods
                if not _test_method_matches(name, test_methods)
            )
            if missing:
                violations.append(
                    f"{path.relative_to(repo_root)}:missing tests {missing} in "
                    f"{test_module_path.relative_to(repo_root)}"
                )

        self.assertEqual([], violations, f"Missing test methods: {violations}")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _should_skip_src_module(path: Path) -> bool:
    return path.name in {"__init__.py", "__main__.py", "_version.py"}


def _required_methods_in_module(path: Path) -> set[str]:
    tree = _parse_tree(path)
    methods = _module_methods(tree)
    return {name for name in methods if not name.startswith("_")}


def _module_methods(tree: ast.AST) -> set[str]:
    methods: set[str] = set()
    if not isinstance(tree, ast.Module):
        return methods
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _is_dunder_method(node.name):
                continue
            methods.add(node.name)
        elif isinstance(node, ast.ClassDef):
            if _is_protocol_class(node):
                continue
            methods.update(_class_methods(node))
    return methods


def _class_methods(class_def: ast.ClassDef) -> set[str]:
    methods: set[str] = set()
    if _is_protocol_class(class_def):
        return methods
    for node in class_def.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _is_dunder_method(node.name):
                continue
            methods.add(node.name)
        elif isinstance(node, ast.ClassDef):
            methods.update(_class_methods(node))
    return methods


def _is_dunder_method(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")


def _is_protocol_class(class_def: ast.ClassDef) -> bool:
    for base in class_def.bases:
        if isinstance(base, ast.Name) and base.id == "Protocol":
            return True
        if isinstance(base, ast.Attribute) and base.attr == "Protocol":
            return True
    return False


def _test_module_path_for_src(path: Path, src_dir: Path, tests_dir: Path) -> Path:
    rel_path = path.relative_to(src_dir)
    module_name = rel_path.stem
    test_file_name = f"test_{module_name}.py"
    return tests_dir / rel_path.parent / test_file_name


def _test_method_names(path: Path) -> set[str]:
    tree = _parse_tree(path)
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            names.add(node.name)
    return names


def _test_method_matches(source_method: str, test_methods: set[str]) -> bool:
    normalized = source_method.lstrip("_")
    required_prefix = f"test_{normalized}"
    for name in test_methods:
        if not name.startswith(required_prefix):
            continue
        if name == required_prefix:
            return True
        if name[len(required_prefix)] == "_":
            return True
    return False


def _parse_tree(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"))
