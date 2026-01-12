import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.docker.pull import run_pull


class DockerPullTests(TestCase):
    def test_run_pull_writes_logs(self) -> None:
        client = mock.Mock()
        client.api.pull.return_value = [{"status": "downloaded"}, b"done\n"]
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with mock.patch("aicage.docker.pull.get_docker_client", return_value=client):
                run_pull("ghcr.io/aicage/aicage:latest", log_path)

            payload = log_path.read_text(encoding="utf-8")
        self.assertIn('"status": "downloaded"', payload)
        self.assertIn("done", payload)
