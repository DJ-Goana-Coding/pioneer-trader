import os
import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import pandas_ta as ta
from dotenv import load_dotenv

load_dotenv()

class VortexEngine:
    def __init__(self):
        # --- CONSTANTS ---
        self.starting_capital = 94.50
        self.min_stake = 10.15
        self.fallback_stake = 10.20
        self.initial_slots = 9
        self.max_slots = 35
        
        # --- VOLATILE STATE (Initialized for HUD Safety) ---
        self.wallet_balance = 0.0
        self.total_profit = 0.0 
        self.total_equity = 0.0
        self.active_slots = self.initial_slots
        self.held_coins = {}
        self.slot_status = []
        
        # --- API SETUP ---
        api_key = os.getenv('BINANCE_API_KEY')
        secret_key = os.getenv('BINANCE_SECRET') or os.getenv('BINANCE_SECRET_KEY')

        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot', 'adjustForTimeDifference': True}
        })

    async def fetch_portfolio(self):
        try:
            # Atomic fetch of balance and equity
            balance = await self.exchange.fetch_balance()
            self.wallet_balance = balance['total'].get('USDT', 0)
            
            holdings = {}
            temp_equity = self.wallet_balance
            for coin, amount in balance['total'].items():
                if amount > 0 and coin not in ['USDT', 'BNB']:
                    try:
                        ticker = await self.exchange.fetch_ticker(f"{coin}/USDT")
                        value = amount * ticker['last']
                        temp_equity += value
                        if value > 1.0: holdings[coin] = f"{amount:.4f}"
                    except: continue
            
            self.total_equity = temp_equity
            self.total_profit = self.total_equity - self.starting_capital
            self.held_coins = holdings
            
            # Growth Engine: Every $10.50 totals 1 Slot
            earned_slots = int(self.total_equity / 10.50)
            self.active_slots = max(self.initial_slots, min(earned_slots, self.max_slots))
        except: pass

    async def execute_trade(self, pair, strategy, rsi):
        # ATOMIC BALANCE SYNC: Final check before firing the bullet
        balance = await self.exchange.fetch_balance()
        current_usdt = balance['total'].get('USDT', 0)
        
        if current_usdt < self.min_stake:
            print(f"🛡️ ATOMIC BLOCK: {pair} aborted. USDT ${current_usdt:.2f} is under ${self.min_stake}.")
            return

        # Attempt 1: $10.15 Strike
        print(f"⚡ {strategy} ATTEMPT 1: {pair} | RSI: {rsi:.2f} | STAKE: ${self.min_stake}")
        try:
             await self.exchange.create_order(
                 symbol=pair, type='market', side='buy', amount=None,
                 params={'quoteOrderQty': self.min_stake}
             )
             print(f"✅ SUCCESS: {pair} BOUGHT ($10.15)")
             return
        except Exception as e:
             # Attempt 2: $10.20 Fallback
             print(f"⚠️ ATTEMPT 1 KNOCKED BACK. ESCALATING...")
             try:
                 await self.exchange.create_order(
                     symbol=pair, type='market', side='buy', amount=None,
                     params={'quoteOrderQty': self.fallback_stake}
                 )
                 print(f"✅ SUCCESS: {pair} BOUGHT ($10.20)")
             except Exception as e2:
                 print(f"❌ TRADE FAILED: {e2}")

    async def start_loop(self):
        print("🔥 VORTEX v4.2.6: SINGLE BULLET PROTOCOL LIVE")
        while True:
            try:
                await self.fetch_portfolio()
                market_pairs = ['SOL/USDT', 'XRP/USDT', 'PEPE/USDT', 'DOGE/USDT', 'BTC/USDT', 
                                'ETH/USDT', 'ADA/USDT', 'BNB/USDT', 'TRX/USDT', 'SUI/USDT']
                
                current_scan_data = []
                for i in range(1, self.active_slots + 1):
                    pair = market_pairs[(i - 1) % len(market_pairs)]
                    try:
                        ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='1m', limit=50)
                        df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
                        rsi = ta.rsi(df['c'], length=14).iloc[-1]
                        
                        triggered = rsi < 55
                        status_msg = "🔴 BUY" if triggered else "HUNTING"
                        print(f"Slot {i:02d} | {pair:<10} | RSI: {rsi:.2f} {status_msg}")
                        
                        current_scan_data.append({"slot": i, "pair": pair, "strategy": "HARVESTER", "rsi": f"{rsi:.2f}", "status": status_msg})

                        if triggered:
                            await self.execute_trade(pair, "HARVESTER", rsi)
                            # WAIT for exchange to sync balance after a buy
                            await asyncio.sleep(2.0) 
                        
                        await asyncio.sleep(0.5)
                    except: continue

                self.slot_status = current_scan_data
                await asyncio.sleep(10)
            except Exception as e:
                print(f"Loop Error: {e}")
                await asyncio.sleep(10)