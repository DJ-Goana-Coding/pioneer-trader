"""
Comprehensive test suite for ExchangeService
Tests initialization, connection modes, data fetching, and order creation
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from backend.services.exchange import ExchangeService


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    with patch('backend.services.exchange.settings') as mock_settings:
        mock_settings.EXECUTION_MODE = "PAPER"
        mock_settings.MEXC_API_KEY = "test_key"
        mock_settings.MEXC_SECRET = "test_secret"
        yield mock_settings


@pytest_asyncio.fixture
async def exchange_service(mock_settings):
    """Create an ExchangeService instance for testing"""
    service = ExchangeService()
    yield service
    if service.exchange:
        await service.shutdown()


class TestExchangeServiceInitialization:
    """Test ExchangeService initialization in different modes"""

    @pytest.mark.asyncio
    async def test_initialize_paper_mode(self, exchange_service, mock_settings):
        """Test initialization in PAPER mode"""
        mock_settings.EXECUTION_MODE = "PAPER"

        with patch('backend.services.exchange.ccxt.mexc') as mock_mexc:
            mock_exchange = AsyncMock()
            mock_exchange.load_markets = AsyncMock()
            mock_exchange.markets = {"BTC/USDT": {}, "ETH/USDT": {}}
            mock_mexc.return_value = mock_exchange

            await exchange_service.initialize()

            assert exchange_service.exchange is not None
            assert exchange_service.mode == "PAPER"
            mock_exchange.load_markets.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_live_mode_without_credentials(self, exchange_service, mock_settings):
        """Test that LIVE mode raises error without credentials"""
        mock_settings.EXECUTION_MODE = "LIVE"
        mock_settings.MEXC_API_KEY = ""
        mock_settings.MEXC_SECRET = ""

        with pytest.raises(ValueError, match="MEXC_API_KEY and MEXC_SECRET must be set"):
            await exchange_service.initialize()

    @pytest.mark.asyncio
    async def test_initialize_live_mode_with_credentials(self, exchange_service, mock_settings):
        """Test initialization in LIVE mode with valid credentials"""
        mock_settings.EXECUTION_MODE = "LIVE"
        mock_settings.MEXC_API_KEY = "valid_key"
        mock_settings.MEXC_SECRET = "valid_secret"

        with patch('backend.services.exchange.ccxt.mexc') as mock_mexc:
            mock_exchange = AsyncMock()
            mock_exchange.load_markets = AsyncMock()
            mock_exchange.markets = {"BTC/USDT": {}}
            mock_mexc.return_value = mock_exchange

            await exchange_service.initialize()

            assert exchange_service.mode == "LIVE"
            mock_exchange.load_markets.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_testnet_mode_falls_back_to_paper(self, exchange_service, mock_settings):
        """Test that TESTNET mode falls back to PAPER (MEXC has no testnet)"""
        mock_settings.EXECUTION_MODE = "TESTNET"

        with patch('backend.services.exchange.ccxt.mexc') as mock_mexc:
            mock_exchange = AsyncMock()
            mock_exchange.load_markets = AsyncMock()
            mock_exchange.markets = {"BTC/USDT": {}}
            mock_mexc.return_value = mock_exchange

            await exchange_service.initialize()

            assert exchange_service.mode == "PAPER"


class TestExchangeServiceDataFetching:
    """Test data fetching methods"""

    @pytest.mark.asyncio
    async def test_fetch_ohlcv(self, exchange_service, mock_settings):
        """Test fetching OHLCV data"""
        with patch('backend.services.exchange.ccxt.mexc') as mock_mexc:
            mock_exchange = AsyncMock()
            mock_exchange.load_markets = AsyncMock()
            mock_exchange.markets = {"BTC/USDT": {}}
            mock_exchange.fetch_ohlcv = AsyncMock(return_value=[
                [1609459200000, 29000, 29500, 28500, 29200, 1000]
            ])
            mock_mexc.return_value = mock_exchange

            await exchange_service.initialize()
            df = await exchange_service.fetch_ohlcv("BTC/USDT", "1h", 100)

            assert len(df) == 1
            assert df.columns.tolist() == ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            assert df['close'].iloc[0] == 29200

    @pytest.mark.asyncio
    async def test_fetch_ticker(self, exchange_service, mock_settings):
        """Test fetching ticker data"""
        with patch('backend.services.exchange.ccxt.mexc') as mock_mexc:
            mock_exchange = AsyncMock()
            mock_exchange.load_markets = AsyncMock()
            mock_exchange.markets = {"BTC/USDT": {}}
            mock_exchange.fetch_ticker = AsyncMock(return_value={
                "symbol": "BTC/USDT",
                "last": 50000.0
            })
            mock_mexc.return_value = mock_exchange

            await exchange_service.initialize()
            ticker = await exchange_service.fetch_ticker("BTC/USDT")

            assert ticker["symbol"] == "BTC/USDT"
            assert ticker["last"] == 50000.0

    @pytest.mark.asyncio
    async def test_fetch_balance(self, exchange_service, mock_settings):
        """Test fetching account balance"""
        with patch('backend.services.exchange.ccxt.mexc') as mock_mexc:
            mock_exchange = AsyncMock()
            mock_exchange.load_markets = AsyncMock()
            mock_exchange.markets = {"BTC/USDT": {}}
            mock_exchange.fetch_balance = AsyncMock(return_value={
                "USDT": {"free": 1000.0, "used": 0.0, "total": 1000.0}
            })
            mock_mexc.return_value = mock_exchange

            await exchange_service.initialize()
            balance = await exchange_service.fetch_balance()

            assert balance["USDT"]["free"] == 1000.0


class TestExchangeServiceOrders:
    """Test order creation methods"""

    @pytest.mark.asyncio
    async def test_create_order_paper_mode(self, exchange_service, mock_settings):
        """Test order creation in PAPER mode returns simulated order"""
        mock_settings.EXECUTION_MODE = "PAPER"

        with patch('backend.services.exchange.ccxt.mexc') as mock_mexc:
            mock_exchange = AsyncMock()
            mock_exchange.load_markets = AsyncMock()
            mock_exchange.markets = {"BTC/USDT": {}}
            mock_mexc.return_value = mock_exchange

            await exchange_service.initialize()
            order = await exchange_service.create_order("BTC/USDT", "market", "buy", 0.01, 50000)

            assert order["symbol"] == "BTC/USDT"
            assert order["side"] == "buy"
            assert order["status"] == "closed"
            assert "Paper Trade" in order["info"]

    @pytest.mark.asyncio
    async def test_create_market_buy_paper_mode(self, exchange_service, mock_settings):
        """Test market buy order creation in PAPER mode"""
        mock_settings.EXECUTION_MODE = "PAPER"

        with patch('backend.services.exchange.ccxt.mexc') as mock_mexc:
            mock_exchange = AsyncMock()
            mock_exchange.load_markets = AsyncMock()
            mock_exchange.markets = {"BTC/USDT": {}}
            mock_mexc.return_value = mock_exchange

            await exchange_service.initialize()
            order = await exchange_service.create_market_buy("BTC/USDT", 100.0)

            assert order["symbol"] == "BTC/USDT"
            assert order["type"] == "market"
            assert order["amount"] == 100.0

    @pytest.mark.asyncio
    async def test_exchange_not_initialized_error(self):
        """Test that methods raise error when exchange not initialized"""
        service = ExchangeService()

        with pytest.raises(Exception, match="Exchange not initialized"):
            await service.fetch_ohlcv("BTC/USDT")

        with pytest.raises(Exception, match="Exchange not initialized"):
            await service.fetch_ticker("BTC/USDT")

        with pytest.raises(Exception, match="Exchange not initialized"):
            await service.create_order("BTC/USDT", "market", "buy", 0.01)


class TestExchangeServiceShutdown:
    """Test service shutdown"""

    @pytest.mark.asyncio
    async def test_shutdown(self, exchange_service, mock_settings):
        """Test that shutdown properly closes exchange connection"""
        with patch('backend.services.exchange.ccxt.mexc') as mock_mexc:
            mock_exchange = AsyncMock()
            mock_exchange.load_markets = AsyncMock()
            mock_exchange.markets = {"BTC/USDT": {}}
            mock_exchange.close = AsyncMock()
            mock_mexc.return_value = mock_exchange

            await exchange_service.initialize()
            await exchange_service.shutdown()

            mock_exchange.close.assert_called_once()
