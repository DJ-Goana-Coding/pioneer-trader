import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import unittest
from unittest.mock import patch, Mock, MagicMock, PropertyMock, AsyncMock


class TestExchangeServiceUnit(unittest.TestCase):
    """Unit tests for ExchangeService paper/live modes."""

    def _run(self, coro):
        """Helper to run async coroutines in tests."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def _make_service(self, mode="PAPER"):
        with patch("backend.services.exchange.settings") as mock_settings:
            mock_settings.EXECUTION_MODE = mode
            mock_settings.MEXC_API_KEY = ""
            mock_settings.MEXC_SECRET = ""
            from backend.services.exchange import ExchangeService
            service = ExchangeService()
        return service

    # -- Initial state -------------------------------------------------------
    def test_initial_exchange_is_none(self):
        service = self._make_service()
        self.assertIsNone(service.exchange)

    # -- PAPER mode create_order ---------------------------------------------
    def test_create_order_paper_returns_paper_trade(self):
        service = self._make_service("PAPER")
        service.exchange = MagicMock()  # simulate initialized
        service.mode = "PAPER"
        result = self._run(service.create_order("BTC/USDT", "market", "buy", 10.0))
        self.assertEqual(result["status"], "closed")
        self.assertIn("Paper Trade", result["info"])

    def test_create_order_paper_includes_correct_fields(self):
        service = self._make_service("PAPER")
        service.exchange = MagicMock()
        service.mode = "PAPER"
        result = self._run(service.create_order("ETH/USDT", "limit", "sell", 5.0, 2000.0))
        self.assertEqual(result["symbol"], "ETH/USDT")
        self.assertEqual(result["side"], "sell")
        self.assertEqual(result["amount"], 5.0)

    # -- PAPER mode create_market_buy ----------------------------------------
    def test_create_market_buy_paper_returns_paper_trade(self):
        service = self._make_service("PAPER")
        service.exchange = MagicMock()
        service.mode = "PAPER"
        result = self._run(service.create_market_buy("BTC/USDT", 50.0))
        self.assertEqual(result["status"], "closed")
        self.assertEqual(result["side"], "buy")
        self.assertIn("Paper Trade", result["info"])

    # -- Uninitialized exchange raises ---------------------------------------
    def test_fetch_ohlcv_raises_if_not_initialized(self):
        service = self._make_service()
        with self.assertRaises(Exception):
            self._run(service.fetch_ohlcv("BTC/USDT"))

    def test_fetch_ticker_raises_if_not_initialized(self):
        service = self._make_service()
        with self.assertRaises(Exception):
            self._run(service.fetch_ticker("BTC/USDT"))

    def test_fetch_balance_raises_if_not_initialized(self):
        service = self._make_service()
        with self.assertRaises(Exception):
            self._run(service.fetch_balance())

    # -- LIVE mode without credentials ---------------------------------------
    def test_initialize_live_without_credentials_raises(self):
        service = self._make_service("LIVE")
        service.mode = "LIVE"
        with patch("backend.services.exchange.settings") as mock_settings:
            mock_settings.MEXC_API_KEY = ""
            mock_settings.MEXC_SECRET = ""
            mock_settings.EXECUTION_MODE = "LIVE"
            with self.assertRaises(ValueError):
                self._run(service.initialize())


if __name__ == "__main__":
    unittest.main()
