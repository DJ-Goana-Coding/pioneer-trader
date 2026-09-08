"""Unit tests for backend/services/agent_audit.py."""
import json
import os
import tempfile
import unittest
from pathlib import Path

from backend.services.agent_audit import AgentAudit


class TestAgentAuditLocalWrite(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "audit.jsonl"
        # forward_to_hub=False to keep this test fully offline.
        self.audit = AgentAudit(audit_path=str(self.path), forward_to_hub=False)

    def tearDown(self):
        self.tmp.cleanup()

    def test_record_writes_jsonl_entry(self):
        entry = self.audit.record(
            action="strike",
            actor="admin",
            payload={"symbol": "BTC/USDT", "side": "buy", "amount": 8.0},
        )
        self.assertEqual(entry["action"], "strike")
        self.assertEqual(entry["actor"], "admin")
        self.assertEqual(entry["status"], "ok")
        self.assertIn("ts", entry)
        self.assertIn("node", entry)

        text = self.path.read_text(encoding="utf-8").strip()
        self.assertEqual(len(text.splitlines()), 1)
        loaded = json.loads(text)
        self.assertEqual(loaded["payload"]["symbol"], "BTC/USDT")

    def test_record_multiple_appends(self):
        self.audit.record(action="a")
        self.audit.record(action="b")
        self.audit.record(action="c")
        lines = self.path.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 3)
        actions = [json.loads(l)["action"] for l in lines]
        self.assertEqual(actions, ["a", "b", "c"])

    def test_record_default_actor_is_system(self):
        entry = self.audit.record(action="background_task")
        self.assertEqual(entry["actor"], "system")
        self.assertEqual(entry["payload"], {})

    def test_forward_disabled_does_not_attempt_network(self):
        # Should not raise even though no event loop is running.
        entry = self.audit.record(action="noop")
        self.assertEqual(entry["status"], "ok")


class TestAgentAuditEnvironmentDefault(unittest.TestCase):
    def test_env_var_overrides_default_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "custom_audit.jsonl")
            old = os.environ.get("AGENT_AUDIT_PATH")
            os.environ["AGENT_AUDIT_PATH"] = target
            os.environ["AGENT_AUDIT_FORWARD"] = "False"
            try:
                audit = AgentAudit()
                self.assertEqual(str(audit.audit_path), target)
                audit.record(action="env_test")
                self.assertTrue(os.path.exists(target))
            finally:
                if old is None:
                    os.environ.pop("AGENT_AUDIT_PATH", None)
                else:
                    os.environ["AGENT_AUDIT_PATH"] = old


if __name__ == "__main__":
    unittest.main()
