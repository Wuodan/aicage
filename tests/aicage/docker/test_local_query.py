from unittest import TestCase, mock

from docker.errors import ImageNotFound

from aicage.docker.query import get_local_repo_digest, local_image_exists
from aicage.docker.types import ImageRefRepository


class FakeImage:
    def __init__(self, repo_digests: object):
        self.attrs = {"RepoDigests": repo_digests}


class FakeImages:
    def __init__(self, image: FakeImage | None):
        self._image = image

    def get(self, image_ref: str) -> FakeImage:
        if self._image is None:
            raise ImageNotFound(image_ref)
        return self._image


class FakeClient:
    def __init__(self, image: FakeImage | None):
        self.images = FakeImages(image)


class LocalQueryTests(TestCase):
    def test_get_local_repo_digest(self) -> None:
        image = ImageRefRepository(image_ref="repo:tag", repository="ghcr.io/aicage/aicage")
        with mock.patch(
            "aicage.docker.query.get_docker_client",
            return_value=FakeClient(None),
        ):
            self.assertIsNone(get_local_repo_digest(image))

        with mock.patch(
            "aicage.docker.query.get_docker_client",
            return_value=FakeClient(FakeImage(repo_digests={"bad": "data"})),
        ):
            self.assertIsNone(get_local_repo_digest(image))

        with mock.patch(
            "aicage.docker.query.get_docker_client",
            return_value=FakeClient(FakeImage(repo_digests=["bad"])),
        ):
            self.assertIsNone(get_local_repo_digest(image))

        payload = ["ghcr.io/aicage/aicage@sha256:deadbeef", "other@sha256:skip"]
        with mock.patch(
            "aicage.docker.query.get_docker_client",
            return_value=FakeClient(FakeImage(repo_digests=payload)),
        ):
            digest = get_local_repo_digest(image)
        self.assertEqual("sha256:deadbeef", digest)

    def test_local_image_exists_true_on_success(self) -> None:
        with mock.patch(
            "aicage.docker.query.get_docker_client",
            return_value=FakeClient(FakeImage(repo_digests=[])),
        ):
            exists = local_image_exists("aicage:claude-ubuntu")
        self.assertTrue(exists)

    def test_local_image_exists_false_on_failure(self) -> None:
        with mock.patch(
            "aicage.docker.query.get_docker_client",
            return_value=FakeClient(None),
        ):
            exists = local_image_exists("aicage:claude-ubuntu")
        self.assertFalse(exists)
