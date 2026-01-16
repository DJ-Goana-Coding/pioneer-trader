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
        self.max_total_slots = 45
        
        self.wallet_balance = 0.0
        self.total_equity = 0.0
        self.held_coins = {}
        self.peak_prices = {}
        self.slot_status = []
        self.emergency_sell_done = False # To ensure we only force-sell once
        
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
            temp_equity = self.wallet_balance
            for coin, amount in balance['total'].items():
                if amount > 0 and coin not in ['USDT', 'BNB', 'LDUSDT']:
                    try:
                        ticker = await self.exchange.fetch_ticker(f"{coin}/USDT")
                        val = amount * ticker['last']
                        temp_equity += val
                        if val > 1.0: 
                            holdings[coin] = {
                                'amount': amount, 
                                'value': val, 
                                'price': ticker['last']
                            }
                    except: continue
            self.total_equity = temp_equity
            self.held_coins = holdings
        except: pass

    async def forced_liquidation(self):
        # Sells 4 coins with the smallest losses to free up USDT
        if self.emergency_sell_done or len(self.held_coins) < 4:
            return
        
        print("⚠️ EMERGENCY: LIQUIDATING 4 SLOTS FOR RECOVERY...")
        # Sort by value (approximation of least loss since we don't have entry prices stored)
        sorted_holdings = sorted(self.held_coins.items(), key=lambda x: x[1]['value'], reverse=True)
        to_sell = sorted_holdings[:4]
        
        for coin, data in to_sell:
            try:
                pair = f"{coin}/USDT"
                await self.exchange.create_market_sell_order(pair, data['amount'])
                print(f"✅ FORCED SELL: {pair} | Recovered ~${data['value']:.2f}")
            except Exception as e:
                print(f"❌ Failed to sell {coin}: {e}")
        
        self.emergency_sell_done = True

    async def start_loop(self):
        print("🔥 VORTEX v4.5.0: FORCED RECOVERY MODE ACTIVE")
        while True:
            try:
                await self.fetch_portfolio()
                
                # --- AUTO-LIQUIDATE ON FIRST RUN ---
                if not self.emergency_sell_done:
                    await self.forced_liquidation()
                    await self.fetch_portfolio() # Refresh balance after sell

                now = datetime.now().strftime('%H:%M:%S')
                print(f"--- [RECOVERY REPORT {now}] ---")
                print(f"💰 WALLET: ${self.wallet_balance:.2f} USDT")
                print(f"📊 EQUITY: ${self.total_equity:.2f}")
                print(f"🏹 ACTIVE SLOTS: {len(self.held_coins)}/{self.initial_slots}")
                print(f"📦 HOLDING: {list(self.held_coins.keys())}")
                print("------------------------------")

                # Strategy Logic
                tickers = await self.exchange.fetch_tickers()
                usdt_markets = [t for t in tickers.values() if t['symbol'].endswith('/USDT') and t['quoteVolume'] > 5000000]
                gainers = sorted(usdt_markets, key=lambda x: x['percentage'], reverse=True)[:15]
                intel_pool = list(set([f"{c}/USDT" for c in self.held_coins.keys()] + [t['symbol'] for t in gainers]))

                for pair in intel_pool:
                    try:
                        ticker = await self.exchange.fetch_ticker(pair)
                        cur_price = ticker['last']
                        coin = pair.split('/')[0]
                        
                        if coin in self.held_coins:
                            # Trailing Sell Logic
                            if coin not in self.peak_prices or cur_price > self.peak_prices[coin]:
                                self.peak_prices[coin] = cur_price
                            peak = self.peak_prices[coin]
                            drop_pct = (peak - cur_price) / peak
                            
                            # Simple RSI check
                            ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='1m', limit=30)
                            df = pd.DataFrame(ohlcv, columns=['ts','o','h','l','c','v'])
                            rsi = ta.rsi(df['c'], length=14).iloc[-1]
                            
                            if rsi > 70 and drop_pct >= self.trail_drop:
                                print(f"💎 HARVESTING PROFIT: {pair}")
                                await self.exchange.create_market_sell_order(pair, self.held_coins[coin]['amount'])
                                del self.peak_prices[coin]
                        
                        elif self.wallet_balance >= self.min_stake and len(self.held_coins) < self.initial_slots:
                            # Entry Logic
                            ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='1m', limit=30)
                            df = pd.DataFrame(ohlcv, columns=['ts','o','h','l','c','v'])
                            rsi = ta.rsi(df['c'], length=14).iloc[-1]
                            
                            if rsi < 50:
                                print(f"🚀 STRIKING: {pair} (RSI: {rsi:.2f})")
                                await self.exchange.create_order(pair, 'market', 'buy', params={'quoteOrderQty': self.min_stake})
                                await asyncio.sleep(2)
                                await self.fetch_portfolio()

                    except: continue
                
                await asyncio.sleep(20)
            except Exception as e:
                print(f"⚠️ Loop Error: {e}")
                await asyncio.sleep(10)