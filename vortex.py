import ccxt
import asyncio
import os
import pandas as pd

class VortexOmega:
    def __init__(self):
        # Establish MEXC Bridge via Environment Variables
        self.exchange = ccxt.mexc({
            'apiKey': os.getenv("MEXC_KEY"),
            'secret': os.getenv("MEXC_SECRET"),
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        # V3.1.0 Constants from Release Notes
        self.POSITION_SIZE_PCT = 0.04  # 4% Rule
        self.MIN_POS = 5.0             # $5 USDT Min
        self.MAX_POS = 15.0            # $15 USDT Max
        self.is_running = False

    async def get_total_equity(self):
        balance = await self.exchange.fetch_balance()
        return balance['total'].get('USDT', 0)

    def calculate_position_size(self, total_equity):
        stake = total_equity * self.POSITION_SIZE_PCT
        return max(self.MIN_POS, min(stake, self.MAX_POS))

    async def execute_trade(self, symbol, side):
        try:
            equity = await self.get_total_equity()
            stake = self.calculate_position_size(equity)
            target = symbol.replace("_", "/")
            
            print(f"💰 Position sizing: Equity=${equity:.2f} -> Stake=${stake:.2f} (4% rule)")
            order = self.exchange.create_order(target, 'market', side, stake)
            return order
        except Exception as e:
            print(f"STRIKE ERROR: {e}")
            return {"error": str(e)}

    async def monitor_market(self, symbol):
        self.is_running = True
        print(f"VORTEX V3.1.0 LIVE: {symbol}")
        while self.is_running:
            try:
                ticker = self.exchange.fetch_ticker(symbol.replace("_", "/"))
                print(f"TICK | {symbol} | PRICE: {ticker['last']}")
                await asyncio.sleep(2)
            except Exception as e:
                print(f"PULSE DROP: {e}")
                await asyncio.sleep(5)
