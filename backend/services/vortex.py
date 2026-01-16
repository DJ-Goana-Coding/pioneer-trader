import os
import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import pandas_ta as ta
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class VortexEngine:
    def __init__(self):
        self.starting_capital = 94.50
        self.min_stake = 10.15
        self.trail_drop = 0.005 
        self.initial_slots = 15
        self.wallet_balance = 0.0
        self.total_equity = 0.0
        self.held_coins = {}
        self.peak_prices = {}
        
        api_key = os.getenv('BINANCE_API_KEY')
        secret_key = os.getenv('BINANCE_SECRET') or os.getenv('BINANCE_SECRET_KEY')
        self.exchange = ccxt.binance({
            'apiKey': api_key, 'secret': secret_key,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })

    async def fetch_portfolio(self):
        try:
            balance = await self.exchange.fetch_balance()
            self.wallet_balance = balance['total'].get('USDT', 0)
            holdings = {}
            for coin, amount in balance['total'].items():
                if amount > 0 and coin not in ['USDT', 'BNB', 'LDUSDT']:
                    try:
                        ticker = await self.exchange.fetch_ticker(f"{coin}/USDT")
                        val = amount * ticker['last']
                        if val > 1.0: holdings[coin] = {'amount': amount, 'value': val}
                    except: continue
            self.held_coins = holdings
        except Exception as e:
            print(f"❌ PORTFOLIO FETCH ERROR: {e}")

    async def start_loop(self):
        print("🔍 VORTEX v4.5.2: DIAGNOSTIC MODE ACTIVE")
        while True:
            try:
                await self.fetch_portfolio()
                now = datetime.now().strftime('%H:%M:%S')
                print(f"--- [DIAGNOSTIC {now}] ---")
                print(f"💰 WALLET: ${self.wallet_balance:.2f} | 📦 HOLDING: {list(self.held_coins.keys())}")
                
                # Fetch only top USDT markets
                tickers = await self.exchange.fetch_tickers()
                targets = [t for t in tickers.values() if t['symbol'].endswith('/USDT') and t['quoteVolume'] > 10000000][:10]

                for t in targets:
                    pair = t['symbol']
                    if pair.split('/')[0] not in self.held_coins and self.wallet_balance > 11:
                        print(f"🚀 ATTEMPTING BUY: {pair}")
                        try:
                            # ATTEMPT MARKET BUY
                            order = await self.exchange.create_order(pair, 'market', 'buy', params={'quoteOrderQty': self.min_stake})
                            print(f"✅ BUY SUCCESS: {pair}")
                        except Exception as e:
                            print(f"❌ BUY FAILED: {pair} | REASON: {e}")
                            await asyncio.sleep(1)
                
                await asyncio.sleep(20)
            except Exception as e:
                print(f"⚠️ MAIN ERROR: {e}")
                await asyncio.sleep(20)