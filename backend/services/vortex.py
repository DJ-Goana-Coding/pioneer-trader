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
        self.trail_drop = 0.005 # 0.5%
        
        # State Management
        self.wallet_balance = 0.0
        self.total_equity = 0.0
        self.total_profit = 0.0
        self.active_slots = 9
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

    async def fetch_market_intelligence(self):
        try:
            # BATCH CALL: Fetch all tickers and your wallet assets
            balance = await self.exchange.fetch_balance()
            tickers = await self.exchange.fetch_tickers()
            
            # 1. Start with coins already in wallet
            intelligence_list = [f"{c}/USDT" for c, a in balance['total'].items() if a > 0 and c != 'USDT' and c != 'BNB']
            
            # 2. Add Top Gainers, Losers, and Hot Volume pairs
            usdt_markets = [t for t in tickers.values() if t['symbol'].endswith('/USDT') and t['quoteVolume'] > 5000000]
            gainers = sorted(usdt_markets, key=lambda x: x['percentage'], reverse=True)[:10]
            losers = sorted(usdt_markets, key=lambda x: x['percentage'])[:10]
            hot = sorted(usdt_markets, key=lambda x: x['quoteVolume'], reverse=True)[:10]
            
            combined = list(set(intelligence_list + [t['symbol'] for t in (gainers + losers + hot)]))
            return combined
        except: return ['BTC/USDT', 'SOL/USDT', 'ETH/USDT']

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
            # Every $10.50 in total value = 1 Slot
            self.active_slots = max(9, int(self.total_equity / 10.50))
        except: pass

    async def execute_trade(self, pair, side, price=0):
        if side == 'buy':
            if self.wallet_balance < self.min_stake: return
            try:
                # Attempt 1: $10.15
                await self.exchange.create_order(symbol=pair, type='market', side='buy', params={'quoteOrderQty': self.min_stake})
                print(f"🚀 OMNI-BUY: {pair} ($10.15)")
            except:
                try:
                    # Attempt 2: $10.20 fallback
                    await self.exchange.create_order(symbol=pair, type='market', side='buy', params={'quoteOrderQty': self.fallback_stake})
                    print(f"🚀 OMNI-BUY: {pair} ($10.20)")
                except: pass
        elif side == 'sell':
            coin = pair.split('/')[0]
            amount = self.held_coins.get(coin)
            if not amount: return
            try:
                await self.exchange.create_market_sell_order(pair, amount)
                if coin in self.peak_prices: del self.peak_prices[coin]
                print(f"💰 TRAIL HARVEST: {pair} AT ${price}")
            except: pass

    async def start_loop(self):
        print("🔥 VORTEX v4.3.1: OMNI-STRAT LIVE")
        while True:
            try:
                await self.fetch_portfolio()
                intel_pool = await self.fetch_market_intelligence()
                
                current_scan_data = []
                filled_slots = 0
                
                for pair in intel_pool:
                    if filled_slots >= self.active_slots: break
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
                            # Update Peak for Trailing Stop
                            if coin not in self.peak_prices or cur_price > self.peak_prices[coin]:
                                self.peak_prices[coin] = cur_price
                            
                            peak = self.peak_prices[coin]
                            drop_pct = (peak - cur_price) / peak
                            
                            if rsi > 70 and drop_pct >= self.trail_drop:
                                status = "🟢 TRAIL EXIT"
                                await self.execute_trade(pair, 'sell', price=cur_price)
                            else:
                                status = f"HOLDING (+{((cur_price/peak)-1)*100:.2f}% off peak)"
                        
                        elif rsi < 55: # Omni-Trigger for any slot
                            status = "🔴 OMNI FIRE"
                            await self.execute_trade(pair, 'buy')
                            filled_slots += 1
                            await asyncio.sleep(2) # Protect balance sync

                        current_scan_data.append({"slot": len(current_scan_data)+1, "pair": pair, "rsi": f"{rsi:.2f}", "status": status})
                        await asyncio.sleep(0.5)
                    except: continue

                self.slot_status = current_scan_data
                await asyncio.sleep(10)
            except: await asyncio.sleep(10)