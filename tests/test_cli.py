import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, mock

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aicage import cli
from aicage.config import ConfigError, GlobalConfig, ProjectConfig, SettingsStore
from aicage.discovery import DiscoveryError, discover_base_aliases


class FakeCompleted:
    def __init__(self, stdout: str = "", stderr: str = "", returncode: int = 0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class ParseCliTests(TestCase):
    def test_parse_with_docker_args(self) -> None:
        dry_run, docker_args, tool, tool_args = cli.parse_cli(
            ["--dry-run", "--network=host", "codex", "--foo"]
        )
        self.assertTrue(dry_run)
        self.assertEqual("--network=host", docker_args)
        self.assertEqual("codex", tool)
        self.assertEqual(["--foo"], tool_args)

    def test_parse_with_separator(self) -> None:
        dry_run, docker_args, tool, tool_args = cli.parse_cli(["--dry-run", "--", "codex", "--bar"])
        self.assertTrue(dry_run)
        self.assertEqual("", docker_args)
        self.assertEqual("codex", tool)
        self.assertEqual(["--bar"], tool_args)

    def test_parse_without_docker_args(self) -> None:
        dry_run, docker_args, tool, tool_args = cli.parse_cli(["codex", "--flag"])
        self.assertFalse(dry_run)
        self.assertEqual("", docker_args)
        self.assertEqual("codex", tool)
        self.assertEqual(["--flag"], tool_args)

    def test_parse_help_exits(self) -> None:
        with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            with self.assertRaises(SystemExit) as ctx:
                cli.parse_cli(["--help"])
        self.assertEqual(0, ctx.exception.code)
        self.assertIn("Usage:", stdout.getvalue())

    def test_parse_requires_arguments(self) -> None:
        with self.assertRaises(cli.CliError):
            cli.parse_cli([])

    def test_parse_requires_tool_after_separator(self) -> None:
        with self.assertRaises(cli.CliError):
            cli.parse_cli(["--"])

    def test_parse_requires_tool_name(self) -> None:
        with self.assertRaises(cli.CliError):
            cli.parse_cli([""])


class DiscoveryTests(TestCase):
    def test_discover_base_aliases_parses_latest(self) -> None:
        payload = {
            "results": [
                {"name": "codex-ubuntu-latest"},
                {"name": "codex-fedora-1.0"},
                {"name": "codex-debian-latest"},
                {"name": "cline-ubuntu-latest"},
            ],
            "next": "",
        }

        class FakeResponse:
            def __enter__(self):
                return io.BytesIO(json.dumps(payload).encode("utf-8"))

            def __exit__(self, exc_type, exc, tb):
                return False

        def fake_urlopen(url: str):  # pylint: disable=unused-argument
            return FakeResponse()

        with mock.patch("urllib.request.urlopen", fake_urlopen):
            aliases = discover_base_aliases("wuodan/aicage", "codex")

        self.assertEqual(["debian", "ubuntu"], aliases)

    def test_discover_base_aliases_http_failure(self) -> None:
        def fake_urlopen(url: str):  # pylint: disable=unused-argument
            raise OSError("network down")

        with mock.patch("urllib.request.urlopen", fake_urlopen):
            with self.assertRaises(DiscoveryError):
                discover_base_aliases("wuodan/aicage", "codex")

    def test_discover_base_aliases_invalid_json(self) -> None:
        class FakeResponse:
            def __enter__(self):
                return io.BytesIO(b"not-json")

            def __exit__(self, exc_type, exc, tb):
                return False

        def fake_urlopen(url: str):  # pylint: disable=unused-argument
            return FakeResponse()

        with mock.patch("urllib.request.urlopen", fake_urlopen):
            with self.assertRaises(DiscoveryError):
                discover_base_aliases("wuodan/aicage", "codex")


class ConfigStoreTests(TestCase):
    def test_global_and_project_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            store = SettingsStore(base_dir=base_dir)
            global_path = store.global_config()
            self.assertTrue(global_path.exists())
            global_data = yaml.safe_load(global_path.read_text())
            self.assertEqual("wuodan/aicage", global_data["image_repository"])

            global_cfg = store.load_global()
            self.assertEqual("wuodan/aicage", global_cfg.repository)
            self.assertEqual("ubuntu", global_cfg.default_base)
            self.assertEqual("", global_cfg.docker_args)
            self.assertEqual({}, global_cfg.tools)

            global_cfg.docker_args = "--network=host"
            global_cfg.tools["codex"] = {"base": "ubuntu"}
            store.save_global(global_cfg)

            reloaded_global = store.load_global()
            self.assertEqual(global_cfg, reloaded_global)
            updated_global = yaml.safe_load(global_path.read_text())
            self.assertEqual("wuodan/aicage", updated_global["image_repository"])
            self.assertEqual("--network=host", updated_global["docker_args"])
            self.assertEqual({"codex": {"base": "ubuntu"}}, updated_global["tools"])

            project_path = base_dir / "project"
            project_path.mkdir(parents=True, exist_ok=True)
            project_cfg = store.load_project(project_path)
            self.assertEqual(ProjectConfig(path=str(project_path), docker_args="", tools={}), project_cfg)

            project_cfg.docker_args = "--add-host=host.docker.internal:host-gateway"
            project_cfg.tools["codex"] = {"base": "fedora"}
            store.save_project(project_path, project_cfg)

            reloaded_project = store.load_project(project_path)
            self.assertEqual(project_cfg, reloaded_project)

            yaml_files = list(store.projects_dir.glob("*.yaml"))
            self.assertEqual(1, len(yaml_files))
            with yaml_files[0].open("r", encoding="utf-8") as handle:
                raw = yaml.safe_load(handle)
            self.assertEqual(project_cfg.to_mapping(), raw)

    def test_load_yaml_reports_parse_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            bad_file = base_dir / "bad.yaml"
            bad_file.write_text("key: [unterminated", encoding="utf-8")
            store = SettingsStore(base_dir=base_dir)
            with self.assertRaises(ConfigError):
                store._load_yaml(bad_file)  # noqa: SLF001


class PromptTests(TestCase):
    def test_prompt_requires_tty(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=False):
            with self.assertRaises(cli.CliError):
                cli.prompt_for_base("codex", "ubuntu", ["ubuntu"])

    def test_prompt_validates_choice(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", return_value="fedora"):
            with self.assertRaises(cli.CliError):
                cli.prompt_for_base("codex", "ubuntu", ["ubuntu"])

    def test_assemble_includes_workspace_mount(self) -> None:
        with mock.patch("aicage.cli.resolve_user_ids", return_value=[]):
            cmd = cli.assemble_docker_run(
                image_ref="wuodan/aicage:codex-ubuntu-latest",
                project_path=Path("/work/project"),
                tool_config_host=Path("/host/.codex"),
                tool_mount_container=Path("/aicage/tool-config"),
                merged_docker_args="--network=host",
                tool_args=["--flag"],
                extra_env=["-e", "AICAGE_TOOL_PATH=~/.codex"],
            )
        self.assertEqual(
            [
                "docker",
                "run",
                "--rm",
                "-it",
                "-e",
                "AICAGE_TOOL_PATH=~/.codex",
                "-v",
                "/work/project:/workspace",
                "-v",
                "/host/.codex:/aicage/tool-config",
                "--network=host",
                "wuodan/aicage:codex-ubuntu-latest",
                "--flag",
            ],
            cmd,
        )


class DockerInvocationTests(TestCase):
    def test_read_tool_label_success(self) -> None:
        completed = FakeCompleted(stdout="/tool/path\n", returncode=0)
        with mock.patch("aicage.cli.subprocess.run", return_value=completed) as run_mock:
            label = cli.read_tool_label("repo:tag", "tool_path")
        self.assertEqual("/tool/path", label)
        run_mock.assert_called_once()

    def test_read_tool_label_errors(self) -> None:
        with mock.patch(
            "aicage.cli.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "docker inspect", stderr="boom"),
        ):
            with self.assertRaises(cli.CliError):
                cli.read_tool_label("repo:tag", "tool_path")

        empty = FakeCompleted(stdout="", returncode=0)
        with mock.patch("aicage.cli.subprocess.run", return_value=empty):
            with self.assertRaises(cli.CliError):
                cli.read_tool_label("repo:tag", "tool_path")

    def test_resolve_user_ids_includes_ids_and_user(self) -> None:
        with mock.patch.dict(os.environ, {"USER": "tester"}, clear=False):
            flags = cli.resolve_user_ids()
        self.assertIn("AICAGE_UID", " ".join(flags))
        self.assertIn("AICAGE_GID", " ".join(flags))
        self.assertIn("AICAGE_USER=tester", " ".join(flags))

    def test_pull_image_success_and_warning(self) -> None:
        pull_ok = FakeCompleted(returncode=0)
        with mock.patch("aicage.cli.subprocess.run", return_value=pull_ok) as run_mock:
            cli.pull_image("repo:tag")
        run_mock.assert_called_once_with(["docker", "pull", "repo:tag"], capture_output=True, text=True)

        pull_fail = FakeCompleted(returncode=1, stderr="timeout")
        inspect_ok = FakeCompleted(returncode=0)
        with mock.patch("aicage.cli.subprocess.run", side_effect=[pull_fail, inspect_ok]):
            with mock.patch("sys.stderr", new_callable=io.StringIO) as stderr:
                cli.pull_image("repo:tag")
        self.assertIn("Warning", stderr.getvalue())

    def test_pull_image_raises_on_missing_local(self) -> None:
        pull_fail = FakeCompleted(returncode=1, stderr="network down", stdout="")
        inspect_fail = FakeCompleted(returncode=1, stderr="missing", stdout="")
        with mock.patch("aicage.cli.subprocess.run", side_effect=[pull_fail, inspect_fail]):
            with self.assertRaises(cli.CliError):
                cli.pull_image("repo:tag")

    def test_discover_local_bases_and_errors(self) -> None:
        list_output = "\n".join(
            [
                "repo:codex-ubuntu-latest",
                "repo:codex-debian-latest",
                "repo:codex-ubuntu-1.0",
                "other:codex-ubuntu-latest",
                "repo:codex-<none>",
            ]
        )
        with mock.patch(
            "aicage.cli.subprocess.run",
            return_value=FakeCompleted(stdout=list_output, returncode=0),
        ):
            aliases = cli.discover_local_bases("repo", "codex")
        self.assertEqual(["debian", "ubuntu"], aliases)

        with mock.patch(
            "aicage.cli.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "docker image ls", stderr="boom"),
        ):
            with self.assertRaises(cli.CliError):
                cli.discover_local_bases("repo", "codex")


class MainFlowTests(TestCase):
    def test_main_uses_project_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir)
            global_cfg = GlobalConfig(
                repository="wuodan/aicage",
                default_base="ubuntu",
                docker_args="--global",
                tools={"codex": {"base": "fedora"}},
            )
            project_cfg = ProjectConfig(
                path=str(project_path),
                docker_args="--project",
                tools={"codex": {"base": "debian"}},
            )

            class FakeStore:
                def __init__(self, global_cfg: GlobalConfig, project_cfg: ProjectConfig) -> None:
                    self._global_cfg = global_cfg
                    self._project_cfg = project_cfg

                def load_global(self) -> GlobalConfig:
                    return self._global_cfg

                def load_project(self, project_realpath: Path) -> ProjectConfig:
                    self.loaded_path = project_realpath
                    return self._project_cfg

                def save_project(self, project_realpath: Path, config: ProjectConfig) -> None:
                    self.saved = (project_realpath, config)

            store = FakeStore(global_cfg, project_cfg)
            with mock.patch("aicage.cli.Path.cwd", return_value=project_path), mock.patch(
                "aicage.cli.parse_cli", return_value=(False, "--cli", "codex", ["--flag"])
            ), mock.patch("aicage.cli.SettingsStore", return_value=store), mock.patch(
                "aicage.cli.pull_image"
            ) as pull_mock, mock.patch(
                "aicage.cli.read_tool_label", return_value=str(project_path / ".codex")
            ), mock.patch(
                "aicage.cli.assemble_docker_run", return_value=["docker", "run", "--flag"]
            ) as assemble_mock, mock.patch("aicage.cli.subprocess.run") as run_mock:
                exit_code = cli.main([])

            self.assertEqual(0, exit_code)
            pull_mock.assert_called_once()
            assemble_mock.assert_called_once()
            run_mock.assert_called_once_with(["docker", "run", "--flag"], check=True)
            self.assertEqual(store.loaded_path, project_path)

    def test_main_prompts_and_saves_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir)
            global_cfg = GlobalConfig(
                repository="wuodan/aicage",
                default_base="ubuntu",
                docker_args="--global",
                tools={},
            )
            project_cfg = ProjectConfig(path=str(project_path), docker_args="--project", tools={})

            class FakeStore:
                def __init__(self, global_cfg: GlobalConfig, project_cfg: ProjectConfig) -> None:
                    self._global_cfg = global_cfg
                    self._project_cfg = project_cfg
                    self.saved = None

                def load_global(self) -> GlobalConfig:
                    return self._global_cfg

                def load_project(self, project_realpath: Path) -> ProjectConfig:
                    self.loaded_path = project_realpath
                    return self._project_cfg

                def save_project(self, project_realpath: Path, config: ProjectConfig) -> None:
                    self.saved = (project_realpath, config)

            store = FakeStore(global_cfg, project_cfg)
            pull_target = str(project_path / ".codex")
            with mock.patch("aicage.cli.Path.cwd", return_value=project_path), mock.patch(
                "aicage.cli.parse_cli", return_value=(True, "--cli", "codex", ["--flag"])
            ), mock.patch("aicage.cli.SettingsStore", return_value=store), mock.patch(
                "aicage.cli.discover_base_aliases", side_effect=DiscoveryError("network down")
            ), mock.patch(
                "aicage.cli.discover_local_bases", return_value=["alpine", "ubuntu"]
            ), mock.patch(
                "aicage.cli.prompt_for_base", return_value="alpine"
            ) as prompt_mock, mock.patch(
                "aicage.cli.pull_image"
            ), mock.patch(
                "aicage.cli.read_tool_label", return_value=pull_target
            ), mock.patch(
                "aicage.cli.assemble_docker_run", return_value=["docker", "run", "cmd"]
            ), mock.patch("sys.stderr", new_callable=io.StringIO) as stderr, mock.patch(
                "sys.stdout", new_callable=io.StringIO
            ) as stdout:
                exit_code = cli.main([])

            self.assertEqual(0, exit_code)
            self.assertIn("Warning", stderr.getvalue())
            self.assertIn("docker run cmd", stdout.getvalue())
            self.assertIsNotNone(store.saved)
            saved_cfg = store.saved[1]
            self.assertEqual("alpine", saved_cfg.tools["codex"]["base"])
            prompt_mock.assert_called_once()

    def test_main_handles_no_available_bases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir)
            global_cfg = GlobalConfig(
                repository="wuodan/aicage",
                default_base="ubuntu",
                docker_args="",
                tools={},
            )
            project_cfg = ProjectConfig(path=str(project_path), docker_args="", tools={})

            class FakeStore:
                def __init__(self, global_cfg: GlobalConfig, project_cfg: ProjectConfig) -> None:
                    self._global_cfg = global_cfg
                    self._project_cfg = project_cfg

                def load_global(self) -> GlobalConfig:
                    return self._global_cfg

                def load_project(self, project_realpath: Path) -> ProjectConfig:
                    return self._project_cfg

                def save_project(self, project_realpath: Path, config: ProjectConfig) -> None:
                    self.saved = (project_realpath, config)

            store = FakeStore(global_cfg, project_cfg)
            with mock.patch("aicage.cli.Path.cwd", return_value=project_path), mock.patch(
                "aicage.cli.parse_cli", return_value=(True, "", "codex", [])
            ), mock.patch("aicage.cli.SettingsStore", return_value=store), mock.patch(
                "aicage.cli.discover_base_aliases", return_value=[]
            ), mock.patch(
                "aicage.cli.discover_local_bases", return_value=[]
            ), mock.patch(
                "sys.stderr", new_callable=io.StringIO
            ) as stderr:
                exit_code = cli.main([])

            self.assertEqual(1, exit_code)
            self.assertIn("No base images found", stderr.getvalue())

    def test_main_keyboard_interrupt(self) -> None:
        with mock.patch("aicage.cli.parse_cli", side_effect=KeyboardInterrupt):
            with mock.patch("sys.stdout", new_callable=io.StringIO):
                exit_code = cli.main([])
        self.assertEqual(130, exit_code)
