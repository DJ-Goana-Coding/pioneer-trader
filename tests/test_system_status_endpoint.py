"""Unit tests for the standardized GET /v1/system/status endpoint."""
import os
import unittest

# Set required env before importing the app.
os.environ.setdefault("MEXC_API_KEY", "test")
os.environ.setdefault("MEXC_SECRET", "test")
os.environ.setdefault("ADMIN_PASSWORD", "test")
os.environ.setdefault("SECRET_KEY", "a" * 32)
os.environ.setdefault("AGENT_AUDIT_FORWARD", "False")

from fastapi.testclient import TestClient  # noqa: E402

from backend.main import app  # noqa: E402


class TestSystemStatusEndpoint(unittest.TestCase):
    def test_returns_200_and_required_fields(self):
        with TestClient(app) as client:
            resp = client.get("/v1/system/status")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        # Contract — every QGTNL node must report these fields.
        for key in (
            "node",
            "status",
            "version",
            "execution_mode",
            "exchange",
            "routers_loaded",
            "services",
            "hub_url",
        ):
            self.assertIn(key, body, f"missing '{key}' in /v1/system/status response")

    def test_node_identity_is_pioneer_trader(self):
        with TestClient(app) as client:
            body = client.get("/v1/system/status").json()
        self.assertEqual(body["node"], "pioneer-trader")
        self.assertEqual(body["status"], "ONLINE")
        self.assertEqual(body["version"], "v1")
        self.assertEqual(body["exchange"], "MEXC")

    def test_routers_loaded_includes_core_set(self):
        with TestClient(app) as client:
            body = client.get("/v1/system/status").json()
        loaded = set(body["routers_loaded"])
        # Every router we register in main.py — including the trade and
        # strategy routers wired via the lifespan handler — must appear
        # here. This is the QGTNL contract used by the Vercel HUD.
        for tag in {
            "auth",
            "telemetry",
            "cockpit",
            "security",
            "trade",
            "strategy",
            "system",
        }:
            self.assertIn(tag, loaded, f"router '{tag}' not advertised by /v1/system/status")

    def test_services_section_keys(self):
        with TestClient(app) as client:
            body = client.get("/v1/system/status").json()
        services = body["services"]
        self.assertIn("exchange_service", services)
        self.assertIn("oms", services)
        self.assertIn("strategy_logic", services)


if __name__ == "__main__":
    unittest.main()
