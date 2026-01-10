import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.docker import build
from aicage.docker.errors import DockerError

from ._fixtures import build_run_config


class LocalBuildRunnerTests(TestCase):
    def test_run_build_invokes_docker(self) -> None:
        with mock.patch(
            "aicage.config.images_metadata.models.find_packaged_path",
            return_value=Path("/tmp/build/Dockerfile"),
        ):
            run_config = build_run_config()
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "logs" / "build.log"
            with (
                mock.patch(
                    "aicage.docker.build.find_packaged_path",
                    return_value=Path("/tmp/build/Dockerfile"),
                ),
                mock.patch(
                    "aicage.docker.build.subprocess.run",
                    return_value=mock.Mock(returncode=0),
                ) as run_mock,
            ):
                build.run_build(
                    run_config=run_config,
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    image_ref="aicage:claude-ubuntu",
                    log_path=log_path,
                )

        run_mock.assert_called_once()
        command = run_mock.call_args.args[0]
        self.assertEqual(
            [
                "docker",
                "build",
                "--no-cache",
                "--file",
                "/tmp/build/Dockerfile",
                "--build-arg",
                "BASE_IMAGE=ghcr.io/aicage/aicage-image-base:ubuntu",
                "--build-arg",
                "AGENT=claude",
                "--tag",
                "aicage:claude-ubuntu",
                "/tmp/build",
            ],
            command,
        )

    def test_run_build_raises_on_failure(self) -> None:
        with mock.patch(
            "aicage.config.images_metadata.models.find_packaged_path",
            return_value=Path("/tmp/build/Dockerfile"),
        ):
            run_config = build_run_config()
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "logs" / "build.log"
            with (
                mock.patch(
                    "aicage.docker.build.find_packaged_path",
                    return_value=Path("/tmp/build/Dockerfile"),
                ),
                mock.patch(
                    "aicage.docker.build.subprocess.run",
                    return_value=mock.Mock(returncode=1),
                ),
                self.assertRaises(DockerError),
            ):
                build.run_build(
                    run_config=run_config,
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    image_ref="aicage:claude-ubuntu",
                    log_path=log_path,
                )
