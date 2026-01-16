import os
import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import pandas_ta as ta
from dotenv import load_dotenv

load_dotenv()

class VortexEngine:
    def __init__(self, active_slots=2):
        self.stake = 10.50
        self.slots = active_slots
        self.pairs = ['SOL/USDT', 'XRP/USDT', 'PEPE/USDT', 'DOGE/USDT']
        self.wallet_balance = 0.0  # <--- NEW: SHARED VARIABLE FOR VERCEL
        
        # KEY LOADING
        api_key = os.getenv('BINANCE_API_KEY')
        secret_key = os.getenv('BINANCE_SECRET') 
        if not secret_key: secret_key = os.getenv('BINANCE_SECRET_KEY')

        # CONNECTION
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot', 'adjustForTimeDifference': True}
        })
        self.exchange.set_sandbox_mode(False)

    async def start_loop(self):
        print("🔥 VORTEX ENGINE: LIVE & BROADCASTING")
        try:
            while True:
                try:
                    # 1. FETCH & STORE BALANCE
                    balance = await self.exchange.fetch_balance()
                    self.wallet_balance = balance['total'].get('USDT', 0) # <--- SAVING IT
                    print(f"💰 WALLET: {self.wallet_balance:.2f} USDT")

                    # 2. SCAN
                    for pair in self.pairs[:self.slots]:
                        ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='1m', limit=50)
                        df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
                        df['rsi'] = ta.rsi(df['c'], length=14)
                        rsi = df['rsi'].iloc[-1]
                        print(f"🔍 {pair} | RSI: {rsi:.2f}")
                        await asyncio.sleep(2)

                    await asyncio.sleep(30)
                except Exception as e:
                    print(f"⚠️ LOOP ERROR: {e}")
                    await asyncio.sleep(30)
        finally:
            await self.exchange.close()