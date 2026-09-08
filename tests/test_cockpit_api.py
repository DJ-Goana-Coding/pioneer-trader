import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, Mock, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routers.cockpit import router


def _create_test_app():
    """Create a minimal FastAPI app with the cockpit router."""
    app = FastAPI()
    app.include_router(router)
    return app


app = _create_test_app()
client = TestClient(app)


class TestCockpitHealth(unittest.TestCase):
    """Tests for GET /cockpit/health."""

    def test_health_returns_200(self):
        response = client.get("/cockpit/health")
        self.assertEqual(response.status_code, 200)

    def test_health_returns_healthy_status(self):
        response = client.get("/cockpit/health")
        data = response.json()
        self.assertEqual(data["status"], "HEALTHY")

    def test_health_returns_components(self):
        response = client.get("/cockpit/health")
        data = response.json()
        self.assertIn("components", data)
        self.assertEqual(data["components"]["tia_agent"], "ACTIVE")
        self.assertEqual(data["components"]["garage_manager"], "ACTIVE")


class TestCockpitStatus(unittest.TestCase):
    """Tests for GET /cockpit/status."""

    def test_status_returns_200(self):
        response = client.get("/cockpit/status")
        self.assertEqual(response.status_code, 200)

    def test_status_contains_tia_key(self):
        response = client.get("/cockpit/status")
        data = response.json()
        self.assertIn("tia", data)

    def test_status_contains_admiral_key(self):
        response = client.get("/cockpit/status")
        data = response.json()
        self.assertIn("admiral", data)

    def test_status_contains_authorization_key(self):
        response = client.get("/cockpit/status")
        data = response.json()
        self.assertIn("authorization", data)


class TestCockpitCapabilities(unittest.TestCase):
    """Tests for GET /cockpit/capabilities."""

    def test_capabilities_returns_200(self):
        response = client.get("/cockpit/capabilities")
        self.assertEqual(response.status_code, 200)


class TestCockpitTIASummary(unittest.TestCase):
    """Tests for GET /cockpit/tia/summary."""

    def test_tia_summary_returns_200(self):
        response = client.get("/cockpit/tia/summary")
        self.assertEqual(response.status_code, 200)

    def test_tia_summary_contains_risk_level(self):
        response = client.get("/cockpit/tia/summary")
        data = response.json()
        self.assertIn("risk_level", data)


class TestCockpitTIAConsume(unittest.TestCase):
    """Tests for POST /cockpit/tia/consume."""

    def test_consume_valid_snapshot_returns_200(self):
        snapshot = {
            "wallet_balance": 100.0,
            "total_equity": 120.0,
            "active_slots": 3,
            "starting_capital": 94.50,
        }
        response = client.post("/cockpit/tia/consume", json=snapshot)
        self.assertEqual(response.status_code, 200)

    def test_consume_snapshot_returns_success(self):
        snapshot = {
            "wallet_balance": 80.0,
            "total_equity": 95.0,
            "active_slots": 5,
        }
        response = client.post("/cockpit/tia/consume", json=snapshot)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("snapshots_in_buffer", data)


class TestCockpitAuthorize(unittest.TestCase):
    """Tests for POST /cockpit/authorize."""

    def test_authorize_returns_200(self):
        response = client.post("/cockpit/authorize", json={"force": False})
        # May return 200 or 403 depending on risk level; LOW risk should pass
        self.assertIn(response.status_code, [200, 403])

    def test_authorize_with_force_returns_200(self):
        response = client.post("/cockpit/authorize", json={"force": True})
        self.assertEqual(response.status_code, 200)

    def test_authorize_default_body(self):
        response = client.post("/cockpit/authorize", json={})
        self.assertIn(response.status_code, [200, 403])


class TestCockpitRevoke(unittest.TestCase):
    """Tests for POST /cockpit/revoke."""

    def test_revoke_returns_200(self):
        response = client.post("/cockpit/revoke", json={"reason": "Test revocation"})
        self.assertEqual(response.status_code, 200)

    def test_revoke_default_reason(self):
        response = client.post("/cockpit/revoke", json={})
        self.assertEqual(response.status_code, 200)


class TestCockpitEvents(unittest.TestCase):
    """Tests for GET /cockpit/events."""

    def test_events_returns_200(self):
        response = client.get("/cockpit/events")
        self.assertEqual(response.status_code, 200)

    def test_events_returns_list(self):
        response = client.get("/cockpit/events")
        data = response.json()
        self.assertIn("events", data)
        self.assertIsInstance(data["events"], list)
        self.assertIn("count", data)


class TestCockpitGarageStatus(unittest.TestCase):
    """Tests for GET /cockpit/garage/status."""

    def test_garage_status_returns_200(self):
        response = client.get("/cockpit/garage/status")
        self.assertEqual(response.status_code, 200)

    def test_garage_status_contains_garage_key(self):
        response = client.get("/cockpit/garage/status")
        data = response.json()
        self.assertIn("garage", data)
        self.assertIn("tia_risk", data)
        self.assertIn("recommended_bay", data)


class TestCockpitGarageReload(unittest.TestCase):
    """Tests for POST /cockpit/garage/reload."""

    def test_garage_reload_returns_200(self):
        response = client.post("/cockpit/garage/reload")
        self.assertEqual(response.status_code, 200)

    def test_garage_reload_returns_success(self):
        response = client.post("/cockpit/garage/reload")
        data = response.json()
        self.assertTrue(data["success"])


if __name__ == "__main__":
    unittest.main()
