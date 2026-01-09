from unittest import TestCase

from aicage.runtime import env_vars


class EnvVarsTests(TestCase):
    def test_constants(self) -> None:
        self.assertEqual("AICAGE_UID", env_vars.AICAGE_UID)
        self.assertEqual("AICAGE_GID", env_vars.AICAGE_GID)
        self.assertEqual("AICAGE_USER", env_vars.AICAGE_USER)
        self.assertEqual("AICAGE_WORKSPACE", env_vars.AICAGE_WORKSPACE)
        self.assertEqual("AICAGE_AGENT_CONFIG_PATH", env_vars.AICAGE_AGENT_CONFIG_PATH)
