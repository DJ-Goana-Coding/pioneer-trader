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
        
        # 1. FETCH KEYS
        api_key = os.environ.get('BINANCE_API_KEY')
        secret_key = os.environ.get('BINANCE_SECRET_KEY')
        
        # 2. DEBUG: PROVE WHICH KEY IS LOADED
        if api_key:
            print(f"🔑 KEY LOADED: {api_key[:4]}...**** (Checking for typos)")
        else:
            print("⚠️ CRITICAL: No API Key found.")

        # 3. FORCE REAL BINANCE CONNECTION
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot', 
                'adjustForTimeDifference': True,  # <--- FIXES SIGNATURE ERRORS
            }
        })
        
        # 4. EXPLICITLY SET TO PRODUCTION (NO SANDBOX)
        self.exchange.set_sandbox_mode(False) 

    async def start_loop(self):
        print("🔥 VORTEX ENGINE: LIVE TRADING MODE ENGAGED")
        print("⏳ SYNCING TIME WITH BINANCE...")
        
        while True:
            try:
                # 5. ATTEMPT TO READ REAL WALLET
                balance = await self.exchange.fetch_balance()
                usdt = balance['total'].get('USDT', 0)
                
                # VICTORY LOG
                print(f"💰 REAL WALLET: {usdt:.2f} USDT")

                # MARKET SCAN
                for pair in self.pairs[:self.slots]:
                    ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='1m', limit=50)
                    df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
                    df['rsi'] = ta.rsi(df['c'], length=14)
                    rsi = df['rsi'].iloc[-1]
                    print(f"🔍 {pair} | RSI: {rsi:.2f}")
                    await asyncio.sleep(2)

                await asyncio.sleep(120) # 2 Minute Loop
                
            except Exception as e:
                print(f"⚠️ ERROR: {e}")
                await asyncio.sleep(60)