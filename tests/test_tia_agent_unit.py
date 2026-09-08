import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, Mock, MagicMock, PropertyMock


class TestTIAAgentUnit(unittest.TestCase):
    """Unit tests for TIAAgent risk analysis engine."""

    def _make_agent(self):
        with patch("backend.services.tia_agent.redis_cache") as mock_redis:
            mock_redis.is_connected.return_value = False
            from backend.services.tia_agent import TIAAgent
            agent = TIAAgent()
        return agent

    # -- Initial state -------------------------------------------------------
    def test_initial_state(self):
        agent = self._make_agent()
        from backend.services.tia_agent import RiskLevel
        self.assertEqual(agent.current_risk, RiskLevel.LOW)
        self.assertEqual(agent.confidence, 1.0)

    # -- consume_aegis -------------------------------------------------------
    def test_consume_aegis_adds_snapshot(self):
        agent = self._make_agent()
        agent.consume_aegis({"wallet_balance": 100})
        self.assertEqual(len(agent.aegis_snapshots), 1)

    def test_consume_aegis_keeps_max_10(self):
        agent = self._make_agent()
        for i in range(15):
            agent.consume_aegis({"wallet_balance": i})
        self.assertEqual(len(agent.aegis_snapshots), 10)

    # -- analyze_risk --------------------------------------------------------
    def test_analyze_risk_low_for_healthy_metrics(self):
        agent = self._make_agent()
        from backend.services.tia_agent import RiskLevel
        snapshot = {"wallet_balance": 100, "active_slots": 3, "total_equity": 95, "starting_capital": 94.5}
        self.assertEqual(agent.analyze_risk(snapshot), RiskLevel.LOW)

    def test_analyze_risk_medium_for_degraded_metrics(self):
        agent = self._make_agent()
        from backend.services.tia_agent import RiskLevel
        snapshot = {"wallet_balance": 15, "active_slots": 10, "total_equity": 85, "starting_capital": 94.5}
        self.assertEqual(agent.analyze_risk(snapshot), RiskLevel.MEDIUM)

    def test_analyze_risk_high_for_critical_metrics(self):
        agent = self._make_agent()
        from backend.services.tia_agent import RiskLevel
        snapshot = {"wallet_balance": 5, "active_slots": 15, "total_equity": 60, "starting_capital": 94.5}
        self.assertEqual(agent.analyze_risk(snapshot), RiskLevel.HIGH)

    def test_analyze_risk_no_snapshot_returns_low(self):
        agent = self._make_agent()
        from backend.services.tia_agent import RiskLevel
        self.assertEqual(agent.analyze_risk(), RiskLevel.LOW)

    # -- produce_summary / confidence ----------------------------------------
    def test_produce_summary_sets_confidence(self):
        agent = self._make_agent()
        with patch("backend.services.tia_agent.redis_cache") as mock_redis:
            mock_redis.is_connected.return_value = False
            summary = agent.produce_summary()
        self.assertIn("confidence", summary)
        self.assertIn("risk_level", summary)

    def test_produce_summary_0_snapshots_confidence_05(self):
        agent = self._make_agent()
        with patch("backend.services.tia_agent.redis_cache") as mock_redis:
            mock_redis.is_connected.return_value = False
            agent.produce_summary()
        self.assertEqual(agent.confidence, 0.5)

    def test_produce_summary_1_snapshot_confidence_07(self):
        agent = self._make_agent()
        agent.consume_aegis({"wallet_balance": 100})
        with patch("backend.services.tia_agent.redis_cache") as mock_redis:
            mock_redis.is_connected.return_value = False
            agent.produce_summary()
        self.assertEqual(agent.confidence, 0.7)

    def test_produce_summary_3_snapshots_confidence_10(self):
        agent = self._make_agent()
        for _ in range(3):
            agent.consume_aegis({"wallet_balance": 100})
        with patch("backend.services.tia_agent.redis_cache") as mock_redis:
            mock_redis.is_connected.return_value = False
            agent.produce_summary()
        self.assertEqual(agent.confidence, 1.0)

    # -- should_authorize_admiral --------------------------------------------
    def test_should_authorize_admiral_true_for_low(self):
        agent = self._make_agent()
        from backend.services.tia_agent import RiskLevel
        agent.current_risk = RiskLevel.LOW
        self.assertTrue(agent.should_authorize_admiral())

    def test_should_authorize_admiral_true_for_medium(self):
        agent = self._make_agent()
        from backend.services.tia_agent import RiskLevel
        agent.current_risk = RiskLevel.MEDIUM
        self.assertTrue(agent.should_authorize_admiral())

    def test_should_authorize_admiral_false_for_high(self):
        agent = self._make_agent()
        from backend.services.tia_agent import RiskLevel
        agent.current_risk = RiskLevel.HIGH
        self.assertFalse(agent.should_authorize_admiral())

    # -- get_status ----------------------------------------------------------
    def test_get_status_structure(self):
        agent = self._make_agent()
        status = agent.get_status()
        self.assertIn("risk_level", status)
        self.assertIn("confidence", status)
        self.assertIn("status", status)
        self.assertIn("message", status)
        self.assertEqual(status["status"], "ACTIVE")

    # -- _get_risk_message ---------------------------------------------------
    def test_get_risk_message_low(self):
        agent = self._make_agent()
        from backend.services.tia_agent import RiskLevel
        agent.current_risk = RiskLevel.LOW
        self.assertIn("green", agent._get_risk_message().lower())

    def test_get_risk_message_medium(self):
        agent = self._make_agent()
        from backend.services.tia_agent import RiskLevel
        agent.current_risk = RiskLevel.MEDIUM
        self.assertIn("elevated", agent._get_risk_message().lower())

    def test_get_risk_message_high(self):
        agent = self._make_agent()
        from backend.services.tia_agent import RiskLevel
        agent.current_risk = RiskLevel.HIGH
        self.assertIn("high risk", agent._get_risk_message().lower())


if __name__ == "__main__":
    unittest.main()
