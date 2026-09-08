import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import json
from unittest.mock import patch, Mock, MagicMock


class TestRedisCacheDisabledMode(unittest.TestCase):
    """Tests for RedisCache when client is None (disabled/disconnected)."""

    def _make_cache(self, client=None):
        with patch.object(
            __import__('backend.services.redis_cache', fromlist=['RedisCache']).RedisCache,
            '_connect',
        ):
            from backend.services.redis_cache import RedisCache
            cache = RedisCache()
            cache.client = client
        return cache

    def test_is_connected_returns_false_when_client_none(self):
        cache = self._make_cache(client=None)
        self.assertFalse(cache.is_connected())

    def test_save_portfolio_state_returns_false_when_client_none(self):
        cache = self._make_cache(client=None)
        result = cache.save_portfolio_state({"balance": 100})
        self.assertFalse(result)

    def test_get_portfolio_state_returns_none_when_client_none(self):
        cache = self._make_cache(client=None)
        self.assertIsNone(cache.get_portfolio_state())

    def test_set_peak_price_safe_when_client_none(self):
        cache = self._make_cache(client=None)
        cache.set_peak_price("BTC/USDT", 50000.0)  # Should not raise

    def test_get_peak_price_returns_none_when_client_none(self):
        cache = self._make_cache(client=None)
        self.assertIsNone(cache.get_peak_price("BTC/USDT"))

    def test_get_all_peaks_returns_empty_dict_when_client_none(self):
        cache = self._make_cache(client=None)
        self.assertEqual(cache.get_all_peaks(), {})

    def test_clear_peak_safe_when_client_none(self):
        cache = self._make_cache(client=None)
        cache.clear_peak("BTC/USDT")  # Should not raise

    def test_log_trade_safe_when_client_none(self):
        cache = self._make_cache(client=None)
        cache.log_trade({"symbol": "BTC/USDT", "side": "buy"})  # Should not raise

    def test_get_trade_history_returns_empty_list_when_client_none(self):
        cache = self._make_cache(client=None)
        self.assertEqual(cache.get_trade_history(), [])

    def test_cache_ticker_safe_when_client_none(self):
        cache = self._make_cache(client=None)
        cache.cache_ticker("BTC/USDT", {"last": 50000})  # Should not raise

    def test_get_cached_ticker_returns_none_when_client_none(self):
        cache = self._make_cache(client=None)
        self.assertIsNone(cache.get_cached_ticker("BTC/USDT"))


class TestRedisCacheConnectedMode(unittest.TestCase):
    """Tests for RedisCache with a mock Redis client."""

    def _make_cache_with_mock(self):
        from backend.services.redis_cache import RedisCache
        with patch.object(RedisCache, '_connect'):
            cache = RedisCache()
        cache.client = Mock()
        return cache

    def test_is_connected_returns_true_when_ping_succeeds(self):
        cache = self._make_cache_with_mock()
        cache.client.ping.return_value = True
        self.assertTrue(cache.is_connected())

    def test_is_connected_returns_false_when_ping_raises(self):
        cache = self._make_cache_with_mock()
        cache.client.ping.side_effect = Exception("Connection refused")
        self.assertFalse(cache.is_connected())

    def test_save_portfolio_state_calls_hset(self):
        cache = self._make_cache_with_mock()
        state = {"balance": 100, "positions": ["BTC"]}
        result = cache.save_portfolio_state(state)
        self.assertTrue(result)
        cache.client.hset.assert_called_once()
        cache.client.expire.assert_called_once()

    def test_get_portfolio_state_returns_parsed_data(self):
        cache = self._make_cache_with_mock()
        cache.client.hgetall.return_value = {
            "balance": "100",
            "positions": json.dumps(["BTC"]),
        }
        result = cache.get_portfolio_state()
        self.assertIsNotNone(result)
        self.assertEqual(result["balance"], 100)
        self.assertEqual(result["positions"], ["BTC"])

    def test_get_portfolio_state_returns_none_when_empty(self):
        cache = self._make_cache_with_mock()
        cache.client.hgetall.return_value = {}
        self.assertIsNone(cache.get_portfolio_state())

    def test_set_peak_price_calls_hset(self):
        cache = self._make_cache_with_mock()
        cache.set_peak_price("BTC/USDT", 50000.0)
        cache.client.hset.assert_called_once_with("vortex:peaks", "BTC/USDT", "50000.0")

    def test_get_peak_price_returns_float(self):
        cache = self._make_cache_with_mock()
        cache.client.hget.return_value = "50000.0"
        result = cache.get_peak_price("BTC/USDT")
        self.assertEqual(result, 50000.0)
        self.assertIsInstance(result, float)

    def test_get_peak_price_returns_none_for_missing(self):
        cache = self._make_cache_with_mock()
        cache.client.hget.return_value = None
        self.assertIsNone(cache.get_peak_price("BTC/USDT"))

    def test_get_all_peaks_returns_dict_of_floats(self):
        cache = self._make_cache_with_mock()
        cache.client.hgetall.return_value = {"BTC/USDT": "50000", "ETH/USDT": "3000"}
        result = cache.get_all_peaks()
        self.assertEqual(result, {"BTC/USDT": 50000.0, "ETH/USDT": 3000.0})

    def test_clear_peak_calls_hdel(self):
        cache = self._make_cache_with_mock()
        cache.clear_peak("BTC/USDT")
        cache.client.hdel.assert_called_once_with("vortex:peaks", "BTC/USDT")

    def test_log_trade_calls_lpush(self):
        cache = self._make_cache_with_mock()
        trade = {"symbol": "BTC/USDT", "side": "buy", "amount": 0.001}
        cache.log_trade(trade)
        cache.client.lpush.assert_called_once()
        cache.client.ltrim.assert_called_once_with("vortex:trades", 0, 99)

    def test_get_trade_history_returns_parsed_json_list(self):
        cache = self._make_cache_with_mock()
        trade1 = json.dumps({"symbol": "BTC/USDT", "side": "buy"})
        trade2 = json.dumps({"symbol": "ETH/USDT", "side": "sell"})
        cache.client.lrange.return_value = [trade1, trade2]
        result = cache.get_trade_history(limit=10)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["symbol"], "BTC/USDT")
        self.assertEqual(result[1]["side"], "sell")

    def test_get_trade_history_returns_empty_on_exception(self):
        cache = self._make_cache_with_mock()
        cache.client.lrange.side_effect = Exception("error")
        result = cache.get_trade_history()
        self.assertEqual(result, [])

    def test_cache_ticker_calls_setex(self):
        cache = self._make_cache_with_mock()
        data = {"last": 50000, "bid": 49999}
        cache.cache_ticker("BTC/USDT", data, ttl=15)
        cache.client.setex.assert_called_once_with(
            "ticker:BTC/USDT", 15, json.dumps(data)
        )

    def test_get_cached_ticker_returns_parsed_json(self):
        cache = self._make_cache_with_mock()
        data = {"last": 50000, "bid": 49999}
        cache.client.get.return_value = json.dumps(data)
        result = cache.get_cached_ticker("BTC/USDT")
        self.assertEqual(result, data)

    def test_get_cached_ticker_returns_none_when_miss(self):
        cache = self._make_cache_with_mock()
        cache.client.get.return_value = None
        self.assertIsNone(cache.get_cached_ticker("BTC/USDT"))


if __name__ == "__main__":
    unittest.main()
