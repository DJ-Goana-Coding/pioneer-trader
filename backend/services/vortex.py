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
        
        # ⚠️ FIX: ALIGNING WITH YOUR KEYS
        # We are looking for 'BINANCE_SECRET' (Not _KEY)
        api_key = os.environ.get('BINANCE_API_KEY')
        secret_key = os.environ.get('BINANCE_SECRET') 

        if not api_key or not secret_key:
            print("⚠️ CRITICAL: BINANCE_SECRET or API_KEY missing.")

        # LIVE CONNECTION
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot', 
                'adjustForTimeDifference': True, 
            }
        })
        self.exchange.set_sandbox_mode(False)

    async def start_loop(self):
        print("🔥 VORTEX ENGINE: LIVE TRADING MODE (USING BINANCE_SECRET)")
        
        while True:
            try:
                # 1. CHECK WALLET
                balance = await self.exchange.fetch_balance()
                usdt = balance['total'].get('USDT', 0)
                print(f"💰 WALLET: {usdt:.2f} USDT")

                # 2. SCAN MARKET
                for pair in self.pairs[:self.slots]:
                    ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='1m', limit=50)
                    df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
                    df['rsi'] = ta.rsi(df['c'], length=14)
                    rsi = df['rsi'].iloc[-1]
                    print(f"🔍 {pair} | RSI: {rsi:.2f}")
                    await asyncio.sleep(2)

                await asyncio.sleep(60)
                
            except Exception as e:
                print(f"⚠️ ERROR: {e}")
                await asyncio.sleep(60)