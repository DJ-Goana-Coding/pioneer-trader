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
        exchange_config = {
            'apiKey': settings.BINANCE_API_KEY,
            'secret': settings.BINANCE_SECRET_KEY,
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        }
        
        if self.mode == "TESTNET":
            self.exchange = ccxt.binance(exchange_config)
            self.exchange.set_sandbox_mode(True)
        elif self.mode == "LIVE":
            self.exchange = ccxt.binance(exchange_config)
        else: # PAPER
            # For PAPER, we still use the exchange for data, but we won't execute real trades
            # We might want to use a public client or just the same client but be careful in OMS
            self.exchange = ccxt.binance({'enableRateLimit': True, 'options': {'defaultType': 'future'}})
            
        await self.exchange.load_markets()
        logger.info(f"Exchange initialized in {self.mode} mode")

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

    async def create_order(self, symbol: str, type: str, side: str, amount: float, price: float = None):
        if not self.exchange:
            raise Exception("Exchange not initialized")
        
        # In PAPER mode, we mock the execution here or in OMS. 
        # But strictly speaking, the exchange service should just talk to the exchange.
        # If we are in PAPER mode, we shouldn't be calling this for real execution unless we want to test the API (which we don't for paper).
        # So we'll assume OMS handles the "don't call this in paper mode" logic, OR we handle it here.
        # Let's handle it here for safety.
        
        if self.mode == "PAPER":
            return {
                "id": "paper_trade_id",
                "symbol": symbol,
                "type": type,
                "side": side,
                "amount": amount,
                "price": price,
                "status": "closed", # Instant fill for paper
                "info": "Paper Trade"
            }
            
        return await self.exchange.create_order(symbol, type, side, amount, price)
