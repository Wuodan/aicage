from unittest import TestCase

from aicage.runtime import _env_vars


class EnvVarsTests(TestCase):
    def test_constants(self) -> None:
        self.assertEqual("AICAGE_UID", _env_vars.AICAGE_UID)
        self.assertEqual("AICAGE_GID", _env_vars.AICAGE_GID)
        self.assertEqual("AICAGE_USER", _env_vars.AICAGE_USER)
        self.assertEqual("AICAGE_WORKSPACE", _env_vars.AICAGE_WORKSPACE)
        self.assertEqual("AICAGE_TOOL_PATH", _env_vars.AICAGE_TOOL_PATH)
