#!/usr/bin/env python3
"""Unit tests for backend/core/config.py Settings class."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, Mock, MagicMock


class TestSettingsDefaults(unittest.TestCase):
    """Test default values of the Settings model."""

    def setUp(self):
        from backend.core.config import Settings
        self.settings = Settings()

    def test_project_name_default(self):
        self.assertEqual(self.settings.PROJECT_NAME, "Pioneer Trader")

    def test_execution_mode_default(self):
        self.assertEqual(self.settings.EXECUTION_MODE, "PAPER")

    def test_vortex_stake_usdt_default(self):
        self.assertEqual(self.settings.VORTEX_STAKE_USDT, 8.0)

    def test_vortex_stop_loss_pct_default(self):
        self.assertEqual(self.settings.VORTEX_STOP_LOSS_PCT, 0.015)

    def test_redis_url_default(self):
        self.assertEqual(self.settings.REDIS_URL, "redis://localhost:6379")

    def test_redis_enabled_default(self):
        self.assertTrue(self.settings.REDIS_ENABLED)

    def test_max_order_notional_default(self):
        self.assertEqual(self.settings.MAX_ORDER_NOTIONAL, 50.0)

    def test_min_slot_size_default(self):
        self.assertEqual(self.settings.MIN_SLOT_SIZE, 8.0)

    def test_port_default(self):
        self.assertEqual(self.settings.PORT, 7860)

    def test_diagnostic_mode_default(self):
        self.assertTrue(self.settings.DIAGNOSTIC_MODE)

    def test_enable_malware_protection_default(self):
        self.assertTrue(self.settings.ENABLE_MALWARE_PROTECTION)

    def test_enable_github_pages_export_default(self):
        self.assertFalse(self.settings.ENABLE_GITHUB_PAGES_EXPORT)

    def test_admin_username_default(self):
        self.assertEqual(self.settings.ADMIN_USERNAME, "admin")

    def test_access_token_expire_minutes_default(self):
        self.assertEqual(self.settings.ACCESS_TOKEN_EXPIRE_MINUTES, 30)


class TestSettingsInstantiation(unittest.TestCase):
    """Test that Settings can be instantiated."""

    def test_settings_instantiation(self):
        from backend.core.config import Settings
        s = Settings()
        self.assertIsNotNone(s)

    def test_settings_is_pydantic_model(self):
        from backend.core.config import Settings
        from pydantic import BaseModel
        self.assertTrue(issubclass(Settings, BaseModel))


class TestModuleLevelExports(unittest.TestCase):
    """Test module-level exports."""

    def test_mexc_api_key_export(self):
        from backend.core import config
        self.assertIsNotNone(config.MEXC_API_KEY)
        self.assertEqual(config.MEXC_API_KEY, config.settings.MEXC_API_KEY)

    def test_mexc_secret_export(self):
        from backend.core import config
        self.assertIsNotNone(config.MEXC_SECRET)
        self.assertEqual(config.MEXC_SECRET, config.settings.MEXC_SECRET)


if __name__ == "__main__":
    unittest.main()
