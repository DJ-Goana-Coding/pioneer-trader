import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import asyncio
from unittest.mock import patch


class TestStrategyEngineInitialState(unittest.TestCase):
    """Tests for StrategyEngine initial state."""

    def test_initial_exchange_is_none(self):
        from backend.services.strategy_engine import StrategyEngine
        engine = StrategyEngine()
        self.assertIsNone(engine.exchange)

    def test_initial_last_reload(self):
        from backend.services.strategy_engine import StrategyEngine
        engine = StrategyEngine()
        self.assertEqual(engine.last_reload, "Init")

    def test_initial_last_strategy(self):
        from backend.services.strategy_engine import StrategyEngine
        engine = StrategyEngine()
        self.assertEqual(engine.last_strategy, "None")


class TestStrategyEngineReload(unittest.TestCase):
    """Tests for StrategyEngine.reload_strategy."""

    def test_reload_strategy_updates_state(self):
        from backend.services.strategy_engine import StrategyEngine
        engine = StrategyEngine()
        result = asyncio.run(engine.reload_strategy("momentum"))
        self.assertTrue(result)
        self.assertEqual(engine.last_reload, "Success")
        self.assertEqual(engine.last_strategy, "momentum")

    def test_reload_strategy_returns_true(self):
        from backend.services.strategy_engine import StrategyEngine
        engine = StrategyEngine()
        result = asyncio.run(engine.reload_strategy("scalper"))
        self.assertTrue(result)

    def test_reload_strategy_with_different_names(self):
        from backend.services.strategy_engine import StrategyEngine
        engine = StrategyEngine()
        asyncio.run(engine.reload_strategy("alpha"))
        self.assertEqual(engine.last_strategy, "alpha")
        asyncio.run(engine.reload_strategy("beta"))
        self.assertEqual(engine.last_strategy, "beta")


class TestStrategyEngineTelemetry(unittest.TestCase):
    """Tests for StrategyEngine.get_telemetry."""

    @patch.dict(os.environ, {"MEXC_API_KEY": "", "MEXC_SECRET": ""}, clear=False)
    def test_telemetry_blind_when_no_keys(self):
        from backend.services.strategy_engine import StrategyEngine
        engine = StrategyEngine()
        engine.api_key = ""
        engine.secret = ""
        result = asyncio.run(engine.get_telemetry())
        self.assertEqual(result["status"], "Blind")
        self.assertIn("error", result)
        self.assertEqual(result["engine"], "Frankfurt")
        self.assertEqual(result["exchange"], "MEXC")

    @patch.dict(os.environ, {"MEXC_API_KEY": "", "MEXC_SECRET": ""}, clear=False)
    def test_telemetry_blind_when_key_missing(self):
        from backend.services.strategy_engine import StrategyEngine
        engine = StrategyEngine()
        engine.api_key = "somekey"
        engine.secret = ""
        result = asyncio.run(engine.get_telemetry())
        self.assertEqual(result["status"], "Blind")

    @patch.dict(os.environ, {"MEXC_API_KEY": "", "MEXC_SECRET": ""}, clear=False)
    def test_telemetry_blind_when_secret_missing(self):
        from backend.services.strategy_engine import StrategyEngine
        engine = StrategyEngine()
        engine.api_key = ""
        engine.secret = "somesecret"
        result = asyncio.run(engine.get_telemetry())
        self.assertEqual(result["status"], "Blind")


if __name__ == "__main__":
    unittest.main()
