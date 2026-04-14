import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import unittest
from unittest.mock import patch, Mock, MagicMock, PropertyMock
from pathlib import Path


class TestArchivalUnit(unittest.TestCase):
    """Unit tests for ArchivalService trade logging and archival."""

    def _make_service(self, archive_dir):
        with patch("backend.services.archival.settings") as mock_settings:
            mock_settings.SHADOW_ARCHIVE_PATH = str(archive_dir)
            from backend.services.archival import ArchivalService
            service = ArchivalService()
        return service

    def _get_tmpdir(self):
        """Create a temporary directory inside the project for test artifacts."""
        d = Path(os.path.dirname(__file__)) / "_test_archive_tmp"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _cleanup(self, d):
        import shutil
        if d.exists():
            shutil.rmtree(d)

    # -- Initialization ------------------------------------------------------
    def test_initialization_creates_archive_directory(self):
        d = self._get_tmpdir() / "init_test"
        try:
            service = self._make_service(d)
            self.assertTrue(d.exists())
        finally:
            self._cleanup(d)

    # -- log_trade -----------------------------------------------------------
    def test_log_trade_appends_to_trade_logs(self):
        d = self._get_tmpdir() / "log_append"
        try:
            service = self._make_service(d)
            service.log_trade({"symbol": "BTC/USDT", "side": "buy"})
            self.assertEqual(len(service.trade_logs), 1)
        finally:
            self._cleanup(d)

    def test_log_trade_writes_to_jsonl_file(self):
        d = self._get_tmpdir() / "log_jsonl"
        try:
            service = self._make_service(d)
            service.log_trade({"symbol": "BTC/USDT", "side": "buy"})
            jsonl_files = list(d.glob("trades_*.jsonl"))
            self.assertGreaterEqual(len(jsonl_files), 1)
            with open(jsonl_files[0]) as f:
                line = f.readline()
            data = json.loads(line)
            self.assertEqual(data["symbol"], "BTC/USDT")
        finally:
            self._cleanup(d)

    def test_log_trade_adds_timestamp(self):
        d = self._get_tmpdir() / "log_ts"
        try:
            service = self._make_service(d)
            entry = service.log_trade({"symbol": "ETH/USDT"})
            self.assertIn("timestamp", entry)
        finally:
            self._cleanup(d)

    # -- get_recent_logs -----------------------------------------------------
    def test_get_recent_logs_returns_correct_limit(self):
        d = self._get_tmpdir() / "recent_limit"
        try:
            service = self._make_service(d)
            for i in range(10):
                service.log_trade({"id": i})
            logs = service.get_recent_logs(limit=5)
            self.assertEqual(len(logs), 5)
        finally:
            self._cleanup(d)

    def test_get_recent_logs_returns_last_entries(self):
        d = self._get_tmpdir() / "recent_last"
        try:
            service = self._make_service(d)
            for i in range(10):
                service.log_trade({"id": i})
            logs = service.get_recent_logs(limit=3)
            ids = [log["id"] for log in logs]
            self.assertEqual(ids, [7, 8, 9])
        finally:
            self._cleanup(d)

    # -- get_session_stats ---------------------------------------------------
    def test_get_session_stats_no_trades(self):
        d = self._get_tmpdir() / "stats_empty"
        try:
            service = self._make_service(d)
            stats = service.get_session_stats()
            self.assertEqual(stats["total_trades"], 0)
            self.assertEqual(stats["wins"], 0)
            self.assertEqual(stats["losses"], 0)
            self.assertEqual(stats["win_rate"], 0.0)
        finally:
            self._cleanup(d)

    def test_get_session_stats_mixed_wins_losses(self):
        d = self._get_tmpdir() / "stats_mixed"
        try:
            service = self._make_service(d)
            service.log_trade({"status": "WIN"})
            service.log_trade({"status": "WIN"})
            service.log_trade({"status": "LOSS"})
            stats = service.get_session_stats()
            self.assertEqual(stats["wins"], 2)
            self.assertEqual(stats["losses"], 1)
            self.assertEqual(stats["total_trades"], 3)
        finally:
            self._cleanup(d)

    def test_get_session_stats_win_rate_calculation(self):
        d = self._get_tmpdir() / "stats_rate"
        try:
            service = self._make_service(d)
            service.log_trade({"status": "WIN"})
            service.log_trade({"status": "LOSS"})
            service.log_trade({"status": "WIN"})
            service.log_trade({"status": "WIN"})
            stats = service.get_session_stats()
            self.assertAlmostEqual(stats["win_rate"], 75.0)
        finally:
            self._cleanup(d)

    # -- export_for_github_pages ---------------------------------------------
    def test_export_for_github_pages_disabled(self):
        d = self._get_tmpdir() / "export_disabled"
        try:
            with patch("backend.services.archival.settings") as mock_settings:
                mock_settings.SHADOW_ARCHIVE_PATH = str(d)
                mock_settings.ENABLE_GITHUB_PAGES_EXPORT = False
                from backend.services.archival import ArchivalService
                service = ArchivalService()
            result = service.export_for_github_pages()
            self.assertIn("error", result)
        finally:
            self._cleanup(d)

    def test_export_for_github_pages_enabled(self):
        d = self._get_tmpdir() / "export_enabled"
        try:
            with patch("backend.services.archival.settings") as mock_settings:
                mock_settings.SHADOW_ARCHIVE_PATH = str(d)
                mock_settings.ENABLE_GITHUB_PAGES_EXPORT = True
                from backend.services.archival import ArchivalService
                service = ArchivalService()
                result = service.export_for_github_pages()
            self.assertEqual(result["status"], "success")
            self.assertTrue(os.path.exists(result["file"]))
        finally:
            self._cleanup(d)

    # -- get_archive_stats ---------------------------------------------------
    def test_get_archive_stats_returns_file_count(self):
        d = self._get_tmpdir() / "stats_files"
        try:
            service = self._make_service(d)
            service.log_trade({"symbol": "BTC/USDT"})
            stats = service.get_archive_stats()
            self.assertIn("log_files", stats)
            self.assertGreaterEqual(stats["log_files"], 1)
        finally:
            self._cleanup(d)

    def test_get_archive_stats_no_files(self):
        d = self._get_tmpdir() / "stats_nofiles"
        try:
            service = self._make_service(d)
            stats = service.get_archive_stats()
            self.assertEqual(stats["log_files"], 0)
        finally:
            self._cleanup(d)

    @classmethod
    def tearDownClass(cls):
        """Clean up the parent temp directory."""
        import shutil
        d = Path(os.path.dirname(__file__)) / "_test_archive_tmp"
        if d.exists():
            shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()
