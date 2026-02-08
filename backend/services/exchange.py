# ================================================================
# 🔌 EXCHANGE SERVICE - MEXC MIGRATION
# ================================================================
import ccxt.async_support as ccxt
import pandas as pd
from backend.core.config import settings
from backend.core.logging_config import setup_logging

logger = setup_logging("exchange")

class ExchangeService:
    def __init__(self):
        self.exchange = None
        self.mode = settings.EXECUTION_MODE

    async def initialize(self):
        """Initialize MEXC exchange connection"""
        
        # Validate credentials for LIVE mode
        if self.mode == "LIVE":
            if not settings.MEXC_API_KEY or not settings.MEXC_SECRET:
                raise ValueError(
                    "MEXC_API_KEY and MEXC_SECRET must be set for LIVE mode. "
                    "Please configure these in your .env file or set EXECUTION_MODE=PAPER"
                )
            logger.warning("🔥 LIVE MODE ENABLED - Real trading will occur!")
        
        exchange_config = {
            'apiKey': settings.MEXC_API_KEY,
            'secret': settings.MEXC_SECRET,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
                'createMarketBuyOrderRequiresPrice': False
            }
        }
        
        if self.mode == "PAPER":
            self.exchange = ccxt.mexc({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            logger.info("📝 Exchange initialized in PAPER mode (data only)")
            
        elif self.mode == "TESTNET":
            logger.warning("⚠️ MEXC has no testnet - using PAPER mode")
            self.exchange = ccxt.mexc({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            self.mode = "PAPER"
            
        else:
            self.exchange = ccxt.mexc(exchange_config)
            logger.info("🔥 Exchange initialized in LIVE mode")
            
        await self.exchange.load_markets()
        logger.info(f"Exchange initialized in {self.mode} mode")
        logger.info(f"✅ MEXC Markets loaded: {len(self.exchange.markets)} pairs available")

    async def shutdown(self):
        if self.exchange:
            await self.exchange.close()

    async def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100):
        if not self.exchange:
            raise Exception("Exchange not initialized")
        
        ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

    async def fetch_ticker(self, symbol: str):
        if not self.exchange:
            raise Exception("Exchange not initialized")
        return await self.exchange.fetch_ticker(symbol)

    async def fetch_balance(self):
        if not self.exchange:
            raise Exception("Exchange not initialized")
        return await self.exchange.fetch_balance()

    async def create_order(self, symbol: str, type: str, side: str, amount: float, price: float = None):
        if not self.exchange:
            raise Exception("Exchange not initialized")
        
        if self.mode == "PAPER":
            return {
                "id": f"paper_{symbol}_{side}",
                "symbol": symbol,
                "type": type,
                "side": side,
                "amount": amount,
                "price": price,
                "status": "closed",
                "info": "Paper Trade - No real execution"
            }
        
        if type == 'market' and side == 'buy':
            return await self.exchange.create_order(
                symbol=symbol,
                type='market',
                side='buy',
                amount=None,
                params={'quoteOrderQty': amount}
            )
        else:
            return await self.exchange.create_order(symbol, type, side, amount, price)

    async def create_market_buy(self, symbol: str, usdt_amount: float):
        """Create a market buy order using USDT amount"""
        if not self.exchange:
            raise Exception("Exchange not initialized")
        
        if self.mode == "PAPER":
            return {
                "id": f"paper_{symbol}_buy",
                "symbol": symbol,
                "type": "market",
                "side": "buy",
                "amount": usdt_amount,
                "price": None,
                "status": "closed",
                "info": "Paper Trade - No real execution"
            }
        
        return await self.exchange.create_order(
            symbol=symbol,
            type='market',
            side='buy',
            amount=None,
            params={'quoteOrderQty': usdt_amount}
        )
