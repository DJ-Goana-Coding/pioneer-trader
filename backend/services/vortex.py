import os
import asyncio
import ccxt
import pandas as pd
import pandas_ta as ta
import random

class VortexEngine:
    def __init__(self, active_slots=2):
        self.stake = 10.50
        self.slots = active_slots
        self.pairs = ['SOL/USDT', 'XRP/USDT', 'PEPE/USDT', 'DOGE/USDT']
        self.exchange = ccxt.binance({
            'apiKey': os.environ.get('BINANCE_API_KEY'),
            'secret': os.environ.get('BINANCE_SECRET_KEY'),
            'enableRateLimit': True,
        })

    async def start_loop(self):
        # Wait 10-20 seconds on boot to avoid "Teapot" bans
        await asyncio.sleep(random.randint(10, 20))
        print("🌀 VORTEX HEARTBEAT: Stealth mode active.")
        
        while True:
            try:
                balance = await self.exchange.fetch_balance()
                usdt = balance['total'].get('USDT', 0)
                print(f"💰 WALLET: {usdt:.2f} USDT")

                for pair in self.pairs[:self.slots]:
                    ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='1m', limit=50)
                    df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
                    df['rsi'] = ta.rsi(df['c'], length=14)
                    rsi = df['rsi'].iloc[-1]
                    print(f"🔍 {pair} | RSI: {rsi:.2f}")
                    await asyncio.sleep(3) # Space out requests

                # 2-minute gap + random jitter
                await asyncio.sleep(120 + random.randint(1, 15))
            except Exception as e:
                print(f"⚠️ HEARTBEAT PAUSED: {e}")
                await asyncio.sleep(300) # 5 min cool-down on error