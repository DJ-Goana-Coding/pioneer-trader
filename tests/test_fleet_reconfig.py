import time
from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend.services.vortex import VortexBerserker


def _build_ohlcv(prices, volumes=None):
    volumes = volumes or [100] * len(prices)
    return [
        [index, price, price, price, price, volume]
        for index, (price, volume) in enumerate(zip(prices, volumes), start=1)
    ]


@pytest.fixture
def vortex():
    with patch("backend.services.vortex.ccxt.mexc", return_value=Mock(name="mexc")), patch(
        "backend.services.vortex.HfApi", return_value=Mock(name="hf_api")
    ):
        return VortexBerserker()


def test_fleet_configuration(vortex):
    assert vortex.PIRANHA_SLOTS == [1, 2]
    assert vortex.HARVESTER_SLOTS == [3, 4, 5, 6]
    assert vortex.SNIPER_SLOT == [7]


def test_active_slots_preserve_legacy_symbol_writes_without_corrupting_v2_state(vortex):
    canonical_trade = {
        "symbol": "BTC/USDT",
        "entry": 50000.0,
        "qty": 0.001,
        "time": time.time(),
        "wing": vortex.WING_PIRANHA,
        "slot": 1,
        "peak_profit": 0.0,
    }
    vortex.active_trades[1] = canonical_trade.copy()

    vortex.active_slots["BTC/USDT"] = {
        "entry": 49000.0,
        "qty": 0.25,
        "time": time.time(),
        "wing": vortex.WING_HARVESTER,
        "slot": 99,
        "peak_profit": 0.0,
    }

    assert vortex.active_trades[1] == canonical_trade
    assert vortex.active_trades[1]["slot"] == 1
    assert vortex.active_slots["BTC/USDT"]["slot"] == 99
    assert vortex.get_available_slot_type() == (vortex.WING_PIRANHA, 2)


@pytest.mark.asyncio
async def test_execute_exit_supports_legacy_active_slots_without_touching_canonical_slots(vortex, tmp_path):
    vortex.shadow_path = str(tmp_path)
    vortex.active_trades[1] = {
        "symbol": "BTC/USDT",
        "entry": 50000.0,
        "qty": 0.001,
        "time": time.time() - 10,
        "wing": vortex.WING_PIRANHA,
        "slot": 1,
        "peak_profit": 0.0,
    }
    vortex.active_slots["ETH/USDT"] = {
        "symbol": "ETH/USDT",
        "entry": 3000.0,
        "qty": 0.5,
        "time": time.time() - 10,
        "wing": vortex.WING_HARVESTER,
        "slot": 42,
        "peak_profit": 0.0,
    }

    exchange = Mock()
    exchange.fetch_balance = AsyncMock(return_value={"ETH": {"free": 0.5}})
    exchange.create_market_sell_order = AsyncMock(return_value={"id": "sell"})
    vortex.exchange = exchange

    await vortex.execute_exit("ETH/USDT", 0.5, "Legacy Exit")

    exchange.create_market_sell_order.assert_awaited_once_with("ETH/USDT", 0.5)
    assert 1 in vortex.active_trades
    assert "ETH/USDT" not in vortex.active_slots


def test_exchange_and_mexc_attributes_share_one_handle(vortex):
    first_exchange = Mock(name="first_exchange")
    second_exchange = Mock(name="second_exchange")

    vortex.exchange = first_exchange
    assert vortex.mexc is first_exchange

    vortex.mexc = second_exchange
    assert vortex.exchange is second_exchange


@pytest.mark.asyncio
async def test_exchange_patch_is_honored_by_market_entry_and_legacy_candle_methods(vortex):
    exchange = Mock()
    exchange.fetch_tickers = AsyncMock(
        return_value={
            "BTC/USDT": {
                "last": 10.0,
                "open": 9.0,
                "percentage": 8.0,
                "quoteVolume": 6_000_000,
            }
        }
    )
    exchange.fetch_ohlcv = AsyncMock(
        side_effect=[
            _build_ohlcv(list(range(1, 56)), [100] * 54 + [500]),
            _build_ohlcv([10.0, 10.1]),
        ]
    )
    exchange.fetch_ticker = AsyncMock(return_value={"last": 10.0})
    exchange.create_market_buy_order = AsyncMock(return_value={"id": "buy"})
    vortex.exchange = exchange

    movers, sniper_targets = await vortex._scan_market()
    assert movers == [{"symbol": "BTC/USDT", "price": 10.0, "change": 8.0}]
    assert sniper_targets == ["BTC/USDT"]

    assert await vortex._analyze_sniper("BTC/USDT") is True

    await vortex._fill_slot(1, "BTC/USDT", vortex.WING_PIRANHA)
    assert vortex.active_trades[1]["entry"] == 10.0
    assert vortex.active_trades[1]["qty"] == pytest.approx(vortex.base_stake / 10.0)

    candles = await vortex.get_candle_data("BTC/USDT")

    exchange.fetch_ticker.assert_awaited_once_with("BTC/USDT")
    exchange.create_market_buy_order.assert_awaited_once()
    assert exchange.create_market_buy_order.await_args.args[0] == "BTC/USDT"
    assert exchange.create_market_buy_order.await_args.args[1] == pytest.approx(vortex.base_stake / 10.0)
    exchange.fetch_ohlcv.assert_any_await("BTC/USDT", "5m", limit=55)
    exchange.fetch_ohlcv.assert_any_await("BTC/USDT", timeframe="1m", limit=2)
    assert list(candles["close"]) == [10.0, 10.1]


@pytest.mark.asyncio
async def test_exchange_patch_is_honored_by_exit_paths(vortex, tmp_path):
    vortex.shadow_path = str(tmp_path)
    trade = {
        "symbol": "BTC/USDT",
        "entry": 10.0,
        "qty": 0.8,
        "time": time.time() - 10,
        "wing": vortex.WING_PIRANHA,
        "slot": 1,
        "peak_profit": 0.0,
    }
    vortex.active_trades[1] = trade.copy()

    exchange = Mock()
    exchange.fetch_tickers = AsyncMock(return_value={"BTC/USDT": {"last": 10.1}})
    exchange.fetch_balance = AsyncMock(
        side_effect=[
            {"BTC": {"free": 0.8}},
            {"ETH": {"free": 0.5}},
        ]
    )
    exchange.create_market_sell_order = AsyncMock(return_value={"id": "sell"})
    vortex.exchange = exchange

    await vortex._manage_exits()

    exchange.fetch_tickers.assert_awaited_once_with(["BTC/USDT"])
    exchange.create_market_sell_order.assert_any_await("BTC/USDT", 0.8)
    assert 1 not in vortex.active_trades

    manual_trade = {
        "symbol": "ETH/USDT",
        "entry": 20.0,
        "qty": 0.5,
        "time": time.time() - 10,
        "wing": vortex.WING_HARVESTER,
        "slot": 2,
        "peak_profit": 0.0,
    }
    vortex.active_trades[2] = manual_trade

    await vortex._execute_sell(2, manual_trade, "Manual Exit")
    await vortex.force_exit("SOL/USDT", 0.25)

    exchange.create_market_sell_order.assert_any_await("ETH/USDT", 0.5)
    exchange.create_market_sell_order.assert_any_await("SOL/USDT", 0.25)


@pytest.mark.asyncio
async def test_scan_market_requires_exact_usdt_quote(vortex):
    exchange = Mock()
    exchange.fetch_tickers = AsyncMock(
        return_value={
            "BTC/USDT": {
                "last": 10.0,
                "open": 9.5,
                "percentage": 5.0,
                "quoteVolume": 1_000_000,
            },
            "ETH/USDT:USDC": {
                "last": 20.0,
                "open": 19.0,
                "percentage": 8.0,
                "quoteVolume": 9_000_000,
            },
            "SOL/USDC": {
                "last": 30.0,
                "open": 29.0,
                "percentage": 9.0,
                "quoteVolume": 8_000_000,
            },
        }
    )
    vortex.exchange = exchange

    movers, sniper_targets = await vortex._scan_market()

    assert [mover["symbol"] for mover in movers] == ["BTC/USDT"]
    assert sniper_targets == []


@pytest.mark.asyncio
async def test_fill_slot_fetches_only_missing_prices_and_rejects_non_positive_values(vortex):
    exchange = Mock()
    exchange.fetch_ticker = AsyncMock(return_value={"last": 5.0})
    exchange.create_market_buy_order = AsyncMock(return_value={"id": "buy"})
    vortex.exchange = exchange

    await vortex._fill_slot(1, "BTC/USDT", vortex.WING_PIRANHA, price=None)
    exchange.fetch_ticker.assert_awaited_once_with("BTC/USDT")
    assert vortex.active_trades[1]["entry"] == 5.0
    assert exchange.create_market_buy_order.await_args.args[0] == "BTC/USDT"
    assert exchange.create_market_buy_order.await_args.args[1] == pytest.approx(vortex.base_stake / 5.0)

    exchange.fetch_ticker.reset_mock()
    exchange.create_market_buy_order.reset_mock()
    await vortex._fill_slot(2, "ETH/USDT", vortex.WING_HARVESTER, price=2.5)
    exchange.fetch_ticker.assert_not_awaited()
    assert vortex.active_trades[2]["entry"] == 2.5
    assert exchange.create_market_buy_order.await_args.args[0] == "ETH/USDT"
    assert exchange.create_market_buy_order.await_args.args[1] == pytest.approx(vortex.base_stake / 2.5)

    exchange.fetch_ticker.reset_mock()
    exchange.create_market_buy_order.reset_mock()
    await vortex._fill_slot(3, "XRP/USDT", vortex.WING_PIRANHA, price=0)
    await vortex._fill_slot(4, "DOGE/USDT", vortex.WING_PIRANHA, price=-1)
    exchange.fetch_ticker.assert_not_awaited()
    exchange.create_market_buy_order.assert_not_awaited()
    assert 3 not in vortex.active_trades
    assert 4 not in vortex.active_trades

    exchange.fetch_ticker = AsyncMock(return_value={"last": 0.0})
    exchange.create_market_buy_order.reset_mock()
    await vortex._fill_slot(5, "ADA/USDT", vortex.WING_PIRANHA, price=None)
    exchange.fetch_ticker.assert_awaited_once_with("ADA/USDT")
    exchange.create_market_buy_order.assert_not_awaited()
    assert 5 not in vortex.active_trades
