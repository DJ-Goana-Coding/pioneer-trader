#!/usr/bin/env python3
"""Unit tests for backend/core/logging_config.py setup_logging function."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import logging
from unittest.mock import patch, Mock, MagicMock

from backend.core.logging_config import setup_logging


class TestSetupLogging(unittest.TestCase):
    """Test the setup_logging function."""

    def _unique_name(self, suffix):
        return f"test-logger-{id(self)}-{suffix}"

    def test_returns_logger_instance(self):
        name = self._unique_name("returns")
        logger = setup_logging(name=name)
        self.assertIsInstance(logger, logging.Logger)

    def test_logger_has_correct_name(self):
        name = self._unique_name("name")
        logger = setup_logging(name=name)
        self.assertEqual(logger.name, name)

    def test_logger_default_level_info(self):
        name = self._unique_name("info")
        logger = setup_logging(name=name)
        self.assertEqual(logger.level, logging.INFO)

    def test_logger_level_debug(self):
        name = self._unique_name("debug")
        logger = setup_logging(name=name, level="DEBUG")
        self.assertEqual(logger.level, logging.DEBUG)

    def test_logger_has_one_handler(self):
        name = self._unique_name("handler")
        logger = setup_logging(name=name)
        self.assertEqual(len(logger.handlers), 1)

    def test_no_duplicate_handlers(self):
        name = self._unique_name("dup")
        logger1 = setup_logging(name=name)
        logger2 = setup_logging(name=name)
        self.assertIs(logger1, logger2)
        self.assertEqual(len(logger2.handlers), 1)

    def test_logger_propagate_false(self):
        name = self._unique_name("propagate")
        logger = setup_logging(name=name)
        self.assertFalse(logger.propagate)


if __name__ == "__main__":
    unittest.main()
