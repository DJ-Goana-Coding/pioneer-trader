import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, Mock, MagicMock, PropertyMock

from backend.services.admiral_engine import AdmiralEngine, CapabilityType, Capability


class TestAdmiralEngineUnit(unittest.TestCase):
    """Unit tests for AdmiralEngine capability management."""

    def _make_engine(self):
        return AdmiralEngine()

    # -- Initial state -------------------------------------------------------
    def test_initial_premium_not_authorized(self):
        engine = self._make_engine()
        self.assertFalse(engine.premium_authorized)

    def test_base_capabilities_always_enabled(self):
        engine = self._make_engine()
        for name, _ in AdmiralEngine.BASE_CAPABILITIES:
            self.assertTrue(engine.capabilities[name].enabled)

    def test_premium_capabilities_initially_disabled(self):
        engine = self._make_engine()
        for name, _ in AdmiralEngine.PREMIUM_CAPABILITIES:
            self.assertFalse(engine.capabilities[name].enabled)

    # -- grant_premium_access ------------------------------------------------
    def test_grant_premium_enables_premium(self):
        engine = self._make_engine()
        result = engine.grant_premium_access("T.I.A.")
        self.assertTrue(result)
        self.assertTrue(engine.premium_authorized)
        for name, _ in AdmiralEngine.PREMIUM_CAPABILITIES:
            self.assertTrue(engine.capabilities[name].enabled)

    def test_grant_premium_returns_false_if_already_granted(self):
        engine = self._make_engine()
        engine.grant_premium_access("T.I.A.")
        self.assertFalse(engine.grant_premium_access("T.I.A."))

    # -- revoke_premium_access -----------------------------------------------
    def test_revoke_premium_disables_premium(self):
        engine = self._make_engine()
        engine.grant_premium_access("T.I.A.")
        result = engine.revoke_premium_access()
        self.assertTrue(result)
        self.assertFalse(engine.premium_authorized)
        for name, _ in AdmiralEngine.PREMIUM_CAPABILITIES:
            self.assertFalse(engine.capabilities[name].enabled)

    def test_revoke_premium_returns_false_if_already_revoked(self):
        engine = self._make_engine()
        self.assertFalse(engine.revoke_premium_access())

    # -- has_capability ------------------------------------------------------
    def test_has_capability_base(self):
        engine = self._make_engine()
        self.assertTrue(engine.has_capability("basic_trading"))

    def test_has_capability_premium_before_grant(self):
        engine = self._make_engine()
        self.assertFalse(engine.has_capability("sniper_execution"))

    def test_has_capability_premium_after_grant(self):
        engine = self._make_engine()
        engine.grant_premium_access("T.I.A.")
        self.assertTrue(engine.has_capability("sniper_execution"))

    def test_has_capability_nonexistent(self):
        engine = self._make_engine()
        self.assertFalse(engine.has_capability("does_not_exist"))

    # -- get_enabled_capabilities --------------------------------------------
    def test_get_enabled_capabilities_initial_only_base(self):
        engine = self._make_engine()
        enabled = engine.get_enabled_capabilities()
        base_names = [n for n, _ in AdmiralEngine.BASE_CAPABILITIES]
        self.assertEqual(sorted(enabled), sorted(base_names))

    def test_get_enabled_capabilities_after_grant_returns_all(self):
        engine = self._make_engine()
        engine.grant_premium_access("T.I.A.")
        enabled = engine.get_enabled_capabilities()
        total = len(AdmiralEngine.BASE_CAPABILITIES) + len(AdmiralEngine.PREMIUM_CAPABILITIES)
        self.assertEqual(len(enabled), total)

    # -- get_premium_capabilities --------------------------------------------
    def test_get_premium_capabilities_returns_7(self):
        engine = self._make_engine()
        self.assertEqual(len(engine.get_premium_capabilities()), 7)

    # -- get_status ----------------------------------------------------------
    def test_get_status_structure(self):
        engine = self._make_engine()
        status = engine.get_status()
        self.assertIn("status", status)
        self.assertIn("premium_authorized", status)
        self.assertIn("total_capabilities", status)
        self.assertIn("capabilities", status)
        self.assertIn("base", status["capabilities"])
        self.assertIn("premium", status["capabilities"])

    # -- get_capability_summary ----------------------------------------------
    def test_get_capability_summary_structure(self):
        engine = self._make_engine()
        summary = engine.get_capability_summary()
        self.assertIn("premium_authorized", summary)
        self.assertIn("enabled_capabilities", summary)
        self.assertIn("premium_capabilities", summary)

    # -- authorization metadata ----------------------------------------------
    def test_grant_sets_authorization_metadata(self):
        engine = self._make_engine()
        engine.grant_premium_access("TestUser")
        self.assertIsNotNone(engine.authorization_timestamp)
        self.assertEqual(engine.authorized_by, "TestUser")

    def test_revoke_clears_authorization_timestamp(self):
        engine = self._make_engine()
        engine.grant_premium_access("T.I.A.")
        engine.revoke_premium_access()
        self.assertIsNone(engine.authorization_timestamp)


if __name__ == "__main__":
    unittest.main()
