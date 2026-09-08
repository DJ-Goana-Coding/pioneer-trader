import ccxt.async_support as ccxt
import asyncio
import os

class VortexOmega:
    def __init__(self):
        # Initializing MEXC Bridge (async client to avoid blocking the event loop)
        self.exchange = ccxt.mexc({
            'apiKey': os.getenv("MEXC_API_KEY"),
            'secret': os.getenv("MEXC_SECRET"),
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        self.is_running = False

    async def get_balance(self):
        return await self.exchange.fetch_balance()

    async def execute_trade(self, symbol, side, amount):
        try:
            target = symbol.replace("_", "/")
            order = await self.exchange.create_order(target, 'market', side, amount)
            print(f"STRIKE SUCCESS: {side} {amount} {target}")
            return order
        except Exception as e:
            print(f"STRIKE FAILURE: {e}")
            return {"error": str(e)}

    async def monitor_market(self, symbol):
        self.is_running = True
        while self.is_running:
            try:
                ticker = await self.exchange.fetch_ticker(symbol.replace("_", "/"))
                print(f"LIVE | {symbol} | {ticker['last']}")
                await asyncio.sleep(1)
            except Exception as e:
                await asyncio.sleep(5)

    async def close(self):
        """Close the underlying exchange session."""
        try:
            await self.exchange.close()
        except Exception:
            pass
