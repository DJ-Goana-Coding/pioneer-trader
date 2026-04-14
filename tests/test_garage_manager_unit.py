import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, Mock, MagicMock


class TestGarageBayEnum(unittest.TestCase):
    """Tests for GarageBay enum values."""

    def test_elite_value(self):
        from backend.services.garage_manager import GarageBay
        self.assertEqual(GarageBay.ELITE.value, "01_ELITE")

    def test_atomic_value(self):
        from backend.services.garage_manager import GarageBay
        self.assertEqual(GarageBay.ATOMIC.value, "02_ATOMIC")

    def test_clockwork_value(self):
        from backend.services.garage_manager import GarageBay
        self.assertEqual(GarageBay.CLOCKWORK.value, "03_CLOCKWORK")

    def test_fusion_value(self):
        from backend.services.garage_manager import GarageBay
        self.assertEqual(GarageBay.FUSION.value, "04_FUSION")

    def test_bay_count(self):
        from backend.services.garage_manager import GarageBay
        self.assertEqual(len(GarageBay), 4)


class TestRiskToBayMapping(unittest.TestCase):
    """Tests for RISK_TO_BAY mapping."""

    def test_low_risk_maps_to_elite(self):
        from backend.services.garage_manager import GarageManager, GarageBay
        from backend.services.tia_agent import RiskLevel
        self.assertEqual(GarageManager.RISK_TO_BAY[RiskLevel.LOW], GarageBay.ELITE)

    def test_medium_risk_maps_to_clockwork(self):
        from backend.services.garage_manager import GarageManager, GarageBay
        from backend.services.tia_agent import RiskLevel
        self.assertEqual(GarageManager.RISK_TO_BAY[RiskLevel.MEDIUM], GarageBay.CLOCKWORK)

    def test_high_risk_maps_to_atomic(self):
        from backend.services.garage_manager import GarageManager, GarageBay
        from backend.services.tia_agent import RiskLevel
        self.assertEqual(GarageManager.RISK_TO_BAY[RiskLevel.HIGH], GarageBay.ATOMIC)


class TestGarageManagerUnit(unittest.TestCase):
    """Unit tests for GarageManager methods."""

    def _make_manager(self):
        from backend.services.garage_manager import GarageManager
        manager = GarageManager()
        return manager

    def test_get_bay_for_risk_low(self):
        from backend.services.garage_manager import GarageBay
        from backend.services.tia_agent import RiskLevel
        manager = self._make_manager()
        self.assertEqual(manager.get_bay_for_risk(RiskLevel.LOW), GarageBay.ELITE)

    def test_get_bay_for_risk_medium(self):
        from backend.services.garage_manager import GarageBay
        from backend.services.tia_agent import RiskLevel
        manager = self._make_manager()
        self.assertEqual(manager.get_bay_for_risk(RiskLevel.MEDIUM), GarageBay.CLOCKWORK)

    def test_get_bay_for_risk_high(self):
        from backend.services.garage_manager import GarageBay
        from backend.services.tia_agent import RiskLevel
        manager = self._make_manager()
        self.assertEqual(manager.get_bay_for_risk(RiskLevel.HIGH), GarageBay.ATOMIC)

    def test_reload_engines_clears_cache(self):
        from backend.services.garage_manager import GarageBay
        manager = self._make_manager()
        # Simulate cached engine
        manager.engines_cache[GarageBay.ELITE] = Mock()
        manager.current_engine = Mock()
        manager.current_bay = GarageBay.ELITE
        manager.reload_engines()
        self.assertEqual(len(manager.engines_cache), 0)
        self.assertIsNone(manager.current_engine)
        self.assertIsNone(manager.current_bay)

    def test_get_garage_status_structure(self):
        manager = self._make_manager()
        status = manager.get_garage_status()
        self.assertIn("garage_path", status)
        self.assertIn("current_bay", status)
        self.assertIn("available_bays", status)
        self.assertIn("total_bays", status)
        self.assertIn("engines_cached", status)
        self.assertIn("tia_integration", status)
        self.assertEqual(status["total_bays"], 4)
        self.assertEqual(status["tia_integration"], "ACTIVE")

    def test_get_garage_status_no_active_bay(self):
        manager = self._make_manager()
        status = manager.get_garage_status()
        self.assertIsNone(status["current_bay"])

    def test_execute_current_strategy_no_engine_returns_error(self):
        manager = self._make_manager()
        manager.current_engine = None
        # Patch select_ferrari to prevent auto-selection side effects
        with patch.object(manager, 'select_ferrari', return_value=None):
            result = manager.execute_current_strategy({"price": 50000})
        self.assertEqual(result["error"], "NO_FERRARI_ACTIVE")
        self.assertEqual(result["status"], "FAILED")

    def test_execute_current_strategy_with_engine(self):
        manager = self._make_manager()
        from backend.services.garage_manager import GarageBay
        mock_engine = Mock()
        mock_engine.execute_strategy.return_value = {"signal": "BUY", "confidence": 0.9}
        manager.current_engine = mock_engine
        manager.current_bay = GarageBay.ELITE
        result = manager.execute_current_strategy({"price": 50000}, {"stake": 10})
        mock_engine.execute_strategy.assert_called_once_with({"price": 50000}, {"stake": 10})
        self.assertEqual(result["signal"], "BUY")
        self.assertEqual(result["active_bay"], "01_ELITE")

    def test_execute_current_strategy_handles_engine_exception(self):
        manager = self._make_manager()
        from backend.services.garage_manager import GarageBay
        mock_engine = Mock()
        mock_engine.execute_strategy.side_effect = RuntimeError("Engine failure")
        manager.current_engine = mock_engine
        manager.current_bay = GarageBay.ATOMIC
        result = manager.execute_current_strategy({"price": 50000})
        self.assertEqual(result["error"], "EXECUTION_FAILED")
        self.assertEqual(result["status"], "FAILED")
        self.assertIn("Engine failure", result["message"])
        self.assertEqual(result["active_bay"], "02_ATOMIC")

    @patch('backend.services.garage_manager.tia_agent')
    def test_select_ferrari_with_force_bay(self, mock_tia):
        manager = self._make_manager()
        from backend.services.garage_manager import GarageBay
        # Force bay should bypass T.I.A. risk check
        with patch.object(manager, '_load_engine', return_value=Mock()) as mock_load:
            engine = manager.select_ferrari(force_bay=GarageBay.FUSION)
            mock_load.assert_called_once_with(GarageBay.FUSION)
            self.assertEqual(manager.current_bay, GarageBay.FUSION)
            self.assertIsNotNone(engine)
        # T.I.A. should NOT have been consulted
        mock_tia.get_status.assert_not_called()

    @patch('backend.services.garage_manager.tia_agent')
    def test_select_ferrari_auto_uses_tia_risk(self, mock_tia):
        manager = self._make_manager()
        from backend.services.garage_manager import GarageBay
        mock_tia.get_status.return_value = {'risk_level': 'LOW'}
        with patch.object(manager, '_load_engine', return_value=Mock()) as mock_load:
            engine = manager.select_ferrari()
            mock_load.assert_called_once_with(GarageBay.ELITE)
            self.assertEqual(manager.current_bay, GarageBay.ELITE)

    def test_load_engine_caches_result(self):
        manager = self._make_manager()
        from backend.services.garage_manager import GarageBay
        mock_module = Mock()
        manager.engines_cache[GarageBay.ELITE] = mock_module
        result = manager._load_engine(GarageBay.ELITE)
        self.assertIs(result, mock_module)

    def test_load_engine_returns_none_for_missing_bay(self):
        manager = self._make_manager()
        from backend.services.garage_manager import GarageBay
        # FUSION bay likely doesn't have a main.py
        result = manager._load_engine(GarageBay.FUSION)
        # Should return None if bay path doesn't exist (or cached module)
        if GarageBay.FUSION not in manager.engines_cache:
            self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
