import os
import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import pandas_ta as ta
from dotenv import load_dotenv

load_dotenv()

class VortexEngine:
    def __init__(self):
        self.starting_capital = 94.50
        self.min_stake = 10.15
        self.fallback_stake = 10.20
        self.initial_slots = 9
        
        # Trailing Config
        self.trail_drop = 0.005 # 0.5% drop from peak
        self.peak_prices = {} # Track highest price since buy
        
        self.wallet_balance = 0.0
        self.total_profit = 0.0 
        self.total_equity = 0.0
        self.active_slots = self.initial_slots
        self.held_coins = {}
        self.slot_status = []
        
        api_key = os.getenv('BINANCE_API_KEY')
        secret_key = os.getenv('BINANCE_SECRET') or os.getenv('BINANCE_SECRET_KEY')

        self.exchange = ccxt.binance({
            'apiKey': api_key, 'secret': secret_key,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot', 'adjustForTimeDifference': True}
        })

    async def fetch_portfolio(self):
        try:
            balance = await self.exchange.fetch_balance()
            self.wallet_balance = balance['total'].get('USDT', 0)
            holdings = {}
            temp_equity = self.wallet_balance
            for coin, amount in balance['total'].items():
                if amount > 0 and coin not in ['USDT', 'BNB']:
                    try:
                        ticker = await self.exchange.fetch_ticker(f"{coin}/USDT")
                        val = amount * ticker['last']
                        temp_equity += val
                        if val > 1.0: holdings[coin] = amount
                    except: continue
            self.total_equity = temp_equity
            self.total_profit = self.total_equity - self.starting_capital
            self.held_coins = holdings
            self.active_slots = max(self.initial_slots, int(self.total_equity / 10.50))
        except: pass

    async def execute_trade(self, pair, side, rsi, price=0):
        if side == 'buy':
            balance = await self.exchange.fetch_balance()
            if balance['total'].get('USDT', 0) < self.min_stake: return
            try:
                await self.exchange.create_order(symbol=pair, type='market', side='buy', amount=None, params={'quoteOrderQty': self.min_stake})
                print(f"✅ BOUGHT {pair}")
            except:
                try:
                    await self.exchange.create_order(symbol=pair, type='market', side='buy', amount=None, params={'quoteOrderQty': self.fallback_stake})
                    print(f"✅ BOUGHT {pair} (Fallback)")
                except: pass
        
        elif side == 'sell':
            coin = pair.split('/')[0]
            amount = self.held_coins.get(coin)
            if not amount: return
            try:
                await self.exchange.create_market_sell_order(pair, amount)
                if coin in self.peak_prices: del self.peak_prices[coin] # Reset peak
                print(f"💰 TRAIL HARVESTED: {pair} SOLD AT ${price}")
            except Exception as e: print(f"❌ SELL FAILED: {e}")

    async def start_loop(self):
        print("🔥 VORTEX v4.2.8: TRAILING PROFIT LIVE")
        while True:
            try:
                await self.fetch_portfolio()
                market_pairs = ['SOL/USDT', 'XRP/USDT', 'PEPE/USDT', 'DOGE/USDT', 'BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'BNB/USDT', 'TRX/USDT', 'SUI/USDT']
                
                current_scan_data = []
                for i in range(1, self.active_slots + 1):
                    pair = market_pairs[(i - 1) % len(market_pairs)]
                    coin = pair.split('/')[0]
                    try:
                        ticker = await self.exchange.fetch_ticker(pair)
                        cur_price = ticker['last']
                        ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='1m', limit=50)
                        df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
                        rsi = ta.rsi(df['c'], length=14).iloc[-1]
                        
                        is_holding = coin in self.held_coins
                        status = "HUNTING"

                        if is_holding:
                            # Update Peak Price
                            if coin not in self.peak_prices or cur_price > self.peak_prices[coin]:
                                self.peak_prices[coin] = cur_price
                            
                            # Check Trailing Exit (If RSI high AND price dropped 0.5% from peak)
                            peak = self.peak_prices[coin]
                            drop_pct = (peak - cur_price) / peak
                            
                            if rsi > 70 and drop_pct >= self.trail_drop:
                                status = "🟢 TRAIL EXIT"
                                await self.execute_trade(pair, 'sell', rsi, cur_price)
                            else:
                                status = f"HOLDING (+{( (cur_price/peak)-1)*100:.2f}% vs Peak)"
                        
                        elif not is_holding and rsi < 55:
                            status = "🔴 BUY"
                            await self.execute_trade(pair, 'buy', rsi)
                        
                        current_scan_data.append({"slot": i, "pair": pair, "rsi": f"{rsi:.2f}", "status": status})
                        await asyncio.sleep(1)
                    except: continue

                self.slot_status = current_scan_data
                await asyncio.sleep(10)
            except Exception as e:
                await asyncio.sleep(10)