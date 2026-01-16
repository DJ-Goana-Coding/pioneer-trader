import os
import asyncio
import ccxt.async_support as ccxt  # <--- FIX: USING ASYNC LIBRARY
import pandas as pd
import pandas_ta as ta
from dotenv import load_dotenv

# Load the keys from the .env file
load_dotenv()

class VortexEngine:
    def __init__(self, active_slots=2):
        self.stake = 10.50
        self.slots = active_slots
        self.pairs = ['SOL/USDT', 'XRP/USDT', 'PEPE/USDT', 'DOGE/USDT']
        
        # 1. GET KEYS (FROM .ENV FILE)
        api_key = os.getenv('BINANCE_API_KEY')
        secret_key = os.getenv('BINANCE_SECRET') 

        # Fallback
        if not secret_key:
            secret_key = os.getenv('BINANCE_SECRET_KEY')

        if not api_key:
            print("⚠️ CRITICAL: API KEY NOT FOUND IN .ENV")

        # 2. CONNECT
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
        print("🔥 VORTEX ENGINE: LIVE (ASYNC REPAIRED)")
        
        # We must handle closing the connection cleanly
        try:
            while True:
                try:
                    # 3. THIS NOW WORKS BECAUSE WE USED ASYNC_SUPPORT
                    balance = await self.exchange.fetch_balance()
                    usdt = balance['total'].get('USDT', 0)
                    print(f"💰 WALLET: {usdt:.2f} USDT")

                    # Scan Logic
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
        finally:
            await self.exchange.close()