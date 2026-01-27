import subprocess
from unittest import TestCase, mock

from aicage import constants
from aicage.registry import _signature
from aicage.registry._errors import RegistryError


class SignatureVerificationTests(TestCase):
    def test_resolve_verified_digest_returns_digest_ref_on_valid_signature(self) -> None:
        image_ref = "ghcr.io/aicage/aicage:agent"
        with (
            mock.patch(
                "aicage.registry._signature.get_remote_digest",
                return_value="sha256:abc",
            ),
            mock.patch(
                "aicage.registry._signature.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry._signature._run_cosign_verify",
                return_value=subprocess.CompletedProcess(
                    args=["cosign"],
                    returncode=0,
                    stdout="",
                    stderr="",
                ),
            ) as cosign_mock,
        ):
            digest_ref = _signature.resolve_verified_digest(image_ref)
        self.assertEqual("ghcr.io/aicage/aicage@sha256:abc", digest_ref)
        cosign_mock.assert_called_once_with("ghcr.io/aicage/aicage@sha256:abc")

    def test_resolve_verified_digest_raises_on_invalid_signature(self) -> None:
        image_ref = "ghcr.io/aicage/aicage:agent"
        with (
            mock.patch(
                "aicage.registry._signature.get_remote_digest",
                return_value="sha256:abc",
            ),
            mock.patch(
                "aicage.registry._signature.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry._signature._run_cosign_verify",
                return_value=subprocess.CompletedProcess(
                    args=["cosign"],
                    returncode=1,
                    stdout="",
                    stderr="no signatures found",
                ),
            ),
        ):
            with self.assertRaises(RegistryError):
                _signature.resolve_verified_digest(image_ref)

    def test_resolve_verified_digest_raises_on_unknown_error(self) -> None:
        image_ref = "ghcr.io/aicage/aicage:agent"
        with (
            mock.patch(
                "aicage.registry._signature.get_remote_digest",
                return_value="sha256:abc",
            ),
            mock.patch(
                "aicage.registry._signature.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry._signature._run_cosign_verify",
                return_value=subprocess.CompletedProcess(
                    args=["cosign"],
                    returncode=2,
                    stdout="unexpected failure",
                    stderr="",
                ),
            ),
        ):
            with self.assertRaises(RegistryError):
                _signature.resolve_verified_digest(image_ref)

    def test_resolve_verified_digest_raises_when_digest_missing(self) -> None:
        image_ref = "ghcr.io/aicage/aicage:agent"
        with (
            mock.patch(
                "aicage.registry._signature.get_remote_digest",
                return_value=None,
            ) as digest_mock,
            mock.patch(
                "aicage.registry._signature._run_cosign_verify"
            ) as cosign_mock,
        ):
            with self.assertRaises(RegistryError):
                _signature.resolve_verified_digest(image_ref)
        digest_mock.assert_called_once_with(image_ref)
        cosign_mock.assert_not_called()

    def test_resolve_verified_digest_pulls_cosign_image_when_missing(self) -> None:
        image_ref = "ghcr.io/aicage/aicage:agent"
        with (
            mock.patch(
                "aicage.registry._signature.get_remote_digest",
                return_value="sha256:abc",
            ),
            mock.patch(
                "aicage.registry._signature.local_image_exists",
                return_value=False,
            ),
            mock.patch(
                "aicage.registry._signature.pull_log_path",
                return_value=mock.Mock(),
            ) as log_mock,
            mock.patch(
                "aicage.registry._signature.run_pull"
            ) as pull_mock,
            mock.patch(
                "aicage.registry._signature._run_cosign_verify",
                return_value=subprocess.CompletedProcess(
                    args=["cosign"],
                    returncode=0,
                    stdout="",
                    stderr="",
                ),
            ),
        ):
            _signature.resolve_verified_digest(image_ref)
        log_mock.assert_called_once_with(constants.COSIGN_IMAGE_REF)
        pull_mock.assert_called_once_with(constants.COSIGN_IMAGE_REF, log_mock.return_value)
