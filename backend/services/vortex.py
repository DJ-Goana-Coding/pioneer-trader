import os
import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import pandas_ta as ta
from dotenv import load_dotenv

load_dotenv()

class VortexEngine:
    def __init__(self):
        # --- FIXED CONSTANTS ---
        self.starting_capital = 94.50
        self.min_stake = 10.15
        self.fallback_stake = 10.20
        self.trail_drop = 0.005 
        
        # --- ALL HUD VARIABLES (FORCE INITIALIZED) ---
        self.wallet_balance = 0.0
        self.total_equity = 0.0
        self.total_profit = 0.0
        self.active_slots = 9
        self.next_slot_price = 10.50
        self.held_coins = {}
        self.peak_prices = {}
        self.slot_status = []
        
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
                        if val > 1.0: holdings[coin] = amount
                    except: continue
            
            self.total_equity = temp_equity
            self.total_profit = self.total_equity - self.starting_capital
            self.held_coins = holdings
            
            # HUD Logic: 
            raw_slots = int(self.total_equity / 10.50)
            self.active_slots = max(9, min(raw_slots, 35)) 
            self.next_slot_price = (self.active_slots + 1) * 10.50
        except Exception as e:
            print(f"Sync Error: {e}")

    async def execute_trade(self, pair, side, price=0):
        if side == 'buy' and self.wallet_balance >= self.min_stake:
            try:
                await self.exchange.create_order(symbol=pair, type='market', side='buy', params={'quoteOrderQty': self.min_stake})
            except: pass
        elif side == 'sell':
            coin = pair.split('/')[0]
            amount = self.held_coins.get(coin)
            if amount:
                try:
                    await self.exchange.create_market_sell_order(pair, amount)
                    if coin in self.peak_prices: del self.peak_prices[coin]
                except: pass

    async def start_loop(self):
        print("🔥 VORTEX v4.3.5: OMNI-STABLE HUD-FIX LIVE")
        while True:
            try:
                await self.fetch_portfolio()
                tickers = await self.exchange.fetch_tickers()
                usdt_markets = [t for t in tickers.values() if t['symbol'].endswith('/USDT') and t['quoteVolume'] > 5000000]
                gainers = sorted(usdt_markets, key=lambda x: x['percentage'], reverse=True)[:10]
                intel_pool = list(set([f"{c}/USDT" for c in self.held_coins.keys()] + [t['symbol'] for t in gainers]))

                current_scan_data = []
                for i, pair in enumerate(intel_pool):
                    if i >= self.active_slots: break
                    try:
                        ticker = await self.exchange.fetch_ticker(pair)
                        cur_price = ticker['last']
                        coin = pair.split('/')[0]
                        is_holding = coin in self.held_coins
                        
                        ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='1m', limit=50)
                        df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
                        rsi = ta.rsi(df['c'], length=14).iloc[-1]
                        
                        status = "HUNTING"
                        if is_holding:
                            if coin not in self.peak_prices or cur_price > self.peak_prices[coin]:
                                self.peak_prices[coin] = cur_price
                            peak = self.peak_prices[coin]
                            drop_pct = (peak - cur_price) / peak
                            if rsi > 70 and drop_pct >= self.trail_drop:
                                status = "🟢 TRAIL EXIT"
                                await self.execute_trade(pair, 'sell', price=cur_price)
                            else:
                                status = f"HOLD (+{((cur_price/peak)-1)*100:.2f}%)"
                        elif rsi < 55:
                            status = "🔴 OMNI FIRE"
                            await self.execute_trade(pair, 'buy')
                            await asyncio.sleep(2)

                        current_scan_data.append({"slot": i+1, "pair": pair, "rsi": f"{rsi:.2f}", "status": status})
                        await asyncio.sleep(0.5)
                    except: continue

                self.slot_status = current_scan_data
                await asyncio.sleep(10)
            except:
                await asyncio.sleep(10)