import ccxt.async_support as ccxt
import pandas as pd
from backend.core.config import settings

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
            await self.exchange.load_markets()
        elif self.mode == "LIVE":
            self.exchange = ccxt.binance(exchange_config)
            await self.exchange.load_markets()
        else: # PAPER
            # For PAPER, we still use the exchange for data, but we won't execute real trades
            # We might want to use a public client or just the same client but be careful in OMS
            try:
                self.exchange = ccxt.binance({'enableRateLimit': True, 'options': {'defaultType': 'future'}})
                await self.exchange.load_markets()
            except Exception as e:
                # In restricted environments (like CI), we'll operate in mock mode
                print(f"Warning: Could not connect to exchange in PAPER mode: {e}")
                print("Operating in mock mode with simulated data")
                self.exchange = None
            
        print(f"Exchange initialized in {self.mode} mode")

    async def shutdown(self):
        if self.exchange:
            await self.exchange.close()

    async def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100):
        if not self.exchange:
            # Return mock data for testing
            import numpy as np
            from datetime import datetime, timedelta
            
            now = datetime.now()
            timestamps = [(now - timedelta(hours=limit-i)).timestamp() * 1000 for i in range(limit)]
            
            # Generate realistic-looking mock data
            base_price = 50000 if "BTC" in symbol else 3000
            ohlcv = []
            for ts in timestamps:
                open_price = base_price + np.random.randn() * 100
                high = open_price + abs(np.random.randn() * 50)
                low = open_price - abs(np.random.randn() * 50)
                close_price = open_price + np.random.randn() * 75
                volume = abs(np.random.randn() * 1000)
                ohlcv.append([ts, open_price, high, low, close_price, volume])
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        
        ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

    async def fetch_ticker(self, symbol: str):
        if not self.exchange:
            # Return mock ticker
            base_price = 50000 if "BTC" in symbol else 3000
            return {
                'symbol': symbol,
                'last': base_price,
                'bid': base_price - 10,
                'ask': base_price + 10,
                'high': base_price + 100,
                'low': base_price - 100,
                'volume': 10000
            }
            
        return await self.exchange.fetch_ticker(symbol)

    async def create_order(self, symbol: str, type: str, side: str, amount: float, price: float = None):
        if not self.exchange:
            # Mock order execution
            return {
                "id": f"paper_trade_{int(pd.Timestamp.now().timestamp())}",
                "symbol": symbol,
                "type": type,
                "side": side,
                "amount": amount,
                "price": price or (50000 if "BTC" in symbol else 3000),
                "status": "closed",
                "info": "Paper Trade (Mock Mode)"
            }
        
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
