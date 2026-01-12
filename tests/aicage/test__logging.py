from __future__ import annotations

import tempfile
from pathlib import Path
from unittest import TestCase

from aicage import _logging


class LoggingTests(TestCase):
    def test_get_logger(self) -> None:
        logger = _logging.get_logger()
        handlers = list(logger.handlers)
        original_log_path = _logging._LOG_PATH
        try:
            logger.handlers.clear()
            with tempfile.TemporaryDirectory() as temp_dir:
                log_path = Path(temp_dir) / "test.log"
                _logging._LOG_PATH = str(log_path)
                first_logger = _logging.get_logger()
                second_logger = _logging.get_logger()
                self.assertIs(first_logger, second_logger)
                self.assertTrue(first_logger.handlers)
                self.assertTrue(log_path.exists())
        finally:
            logger.handlers.clear()
            logger.handlers.extend(handlers)
            _logging._LOG_PATH = original_log_path
