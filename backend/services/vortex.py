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
        
        # 🔍 DEBUG PRINT: Let's see if the keys are actually being read
        api_key = os.environ.get('BINANCE_API_KEY')
        secret_key = os.environ.get('BINANCE_SECRET_KEY')
        
        if not api_key or not secret_key:
            print("⚠️ CRITICAL: API Keys missing from Environment Variables!")
        else:
            print("🔑 KEYS FOUND: Loading into CCXT Engine...")

        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret_key,  # EXPLICITLY USING BINANCE_SECRET_KEY
            'enableRateLimit': True,
        })

    async def start_loop(self):
        # Stealth Jitter on Boot
        await asyncio.sleep(random.randint(5, 15))
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
                    await asyncio.sleep(2)

                await asyncio.sleep(120 + random.randint(1, 10))
                
            except Exception as e:
                # If signature fails, we print the exact error to diagnose
                print(f"⚠️ HEARTBEAT PAUSED: {e}")
                await asyncio.sleep(60)