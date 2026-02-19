import ccxt
import asyncio
import os

class VortexOmega:
    def __init__(self):
        # Initialize MEXC Bridge via Environment Variables
        self.api_key = os.getenv("MEXC_KEY")
        self.api_secret = os.getenv("MEXC_SECRET")
        
        self.exchange = ccxt.mexc({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        self.is_running = False

    async def get_balance(self):
        return self.exchange.fetch_balance()

    async def execute_trade(self, symbol, side, amount):
        try:
            target = symbol.replace("_", "/")
            print(f"STRIKE: {side} {amount} {target}")
            order = self.exchange.create_order(target, 'market', side, amount)
            return order
        except Exception as e:
            print(f"STRIKE ERROR: {e}")
            return {"error": str(e)}

    async def monitor_market(self, symbol):
        self.is_running = True
        print(f"VORTEX LIVE: {symbol}")
        while self.is_running:
            try:
                ticker = self.exchange.fetch_ticker(symbol.replace("_", "/"))
                print(f"TICK | {symbol} | {ticker['last']}")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"PULSE DROP: {e}")
                await asyncio.sleep(5)
