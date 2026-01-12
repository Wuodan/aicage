from unittest import TestCase

from aicage.registry.digest._parser import parse_image_ref


class DigestParserTests(TestCase):
    def test_parse_image_ref_defaults_to_docker_registry(self) -> None:
        parsed = parse_image_ref("ubuntu:20.04")
        self.assertEqual("registry-1.docker.io", parsed.registry)
        self.assertEqual("library/ubuntu", parsed.repository)
        self.assertEqual("20.04", parsed.reference)
        self.assertFalse(parsed.is_digest)

    def test_parse_image_ref_accepts_explicit_docker_registry(self) -> None:
        parsed = parse_image_ref("docker.io/library/ubuntu:latest")
        self.assertEqual("registry-1.docker.io", parsed.registry)
        self.assertEqual("library/ubuntu", parsed.repository)
        self.assertEqual("latest", parsed.reference)
        self.assertFalse(parsed.is_digest)

    def test_parse_image_ref_accepts_ghcr(self) -> None:
        parsed = parse_image_ref("ghcr.io/org/repo:tag")
        self.assertEqual("ghcr.io", parsed.registry)
        self.assertEqual("org/repo", parsed.repository)
        self.assertEqual("tag", parsed.reference)
        self.assertFalse(parsed.is_digest)

    def test_parse_image_ref_keeps_digest(self) -> None:
        parsed = parse_image_ref("ghcr.io/org/repo@sha256:deadbeef")
        self.assertTrue(parsed.is_digest)
        self.assertEqual("sha256:deadbeef", parsed.reference)

    def test_parse_image_ref_defaults_to_latest_for_explicit_registry(self) -> None:
        parsed = parse_image_ref("ghcr.io/org/repo")
        self.assertEqual("latest", parsed.reference)
        self.assertFalse(parsed.is_digest)

    def test_parse_image_ref_handles_registry_with_port(self) -> None:
        parsed = parse_image_ref("localhost:5000/org/repo:1.2.3")
        self.assertEqual("localhost:5000", parsed.registry)
        self.assertEqual("org/repo", parsed.repository)
        self.assertEqual("1.2.3", parsed.reference)

    def test_parse_image_ref_normalizes_docker_io_alias(self) -> None:
        parsed = parse_image_ref("docker.io/ubuntu:latest")
        self.assertEqual("registry-1.docker.io", parsed.registry)
        self.assertEqual("library/ubuntu", parsed.repository)

    def test_parse_image_ref_handles_empty_digest_reference(self) -> None:
        parsed = parse_image_ref("ghcr.io/org/repo@")
        self.assertTrue(parsed.is_digest)
        self.assertEqual("", parsed.reference)
