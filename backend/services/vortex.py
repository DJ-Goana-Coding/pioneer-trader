import os
import asyncio
import ccxt
import pandas as pd
import pandas_ta as ta
from dotenv import load_dotenv # <--- NEW: LOADS THE FILE

# Load the secrets file immediately
load_dotenv()

class VortexEngine:
    def __init__(self, active_slots=2):
        self.stake = 10.50
        self.slots = active_slots
        self.pairs = ['SOL/USDT', 'XRP/USDT', 'PEPE/USDT', 'DOGE/USDT']
        
        # 1. GET KEYS FROM THE FILE
        api_key = os.getenv('BINANCE_API_KEY')
        secret_key = os.getenv('BINANCE_SECRET')
        
        # Fallback for naming confusion
        if not secret_key:
            secret_key = os.getenv('BINANCE_SECRET_KEY')

        if not api_key:
            print("❌ CRITICAL: NO API KEY FOUND IN .ENV FILE")

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
        print("🔥 VORTEX ENGINE: LIVE (LOADING KEYS FROM .ENV FILE)")
        
        while True:
            try:
                balance = await self.exchange.fetch_balance()
                usdt = balance['total'].get('USDT', 0)
                print(f"💰 WALLET: {usdt:.2f} USDT")

                for pair in self.pairs[:self.slots]:
                    print(f"🔍 SCANNING {pair}...")
                    await asyncio.sleep(1)

                await asyncio.sleep(60)
            except Exception as e:
                print(f"⚠️ ERROR: {e}")
                await asyncio.sleep(60)