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
        self.max_allowed_stake = 10.50
        self.initial_slots = 9
        self.max_slots = 35
        
        self.wallet_balance = 0.0
        self.total_equity = 0.0
        self.active_slots = self.initial_slots
        self.held_coins = {}
        self.slot_status = []
        
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
            self.held_coins = holdings
            
            # Growth: Every $10.50 in total value unlocks a new slot
            earned_slots = int(self.total_equity / 10.50)
            self.active_slots = max(self.initial_slots, min(earned_slots, self.max_slots))
            
        except Exception as e:
            print(f"Sync Error: {e}")

    async def execute_trade(self, pair, strategy, rsi):
        await self.fetch_portfolio()
        if self.wallet_balance < self.min_stake:
            return

        # STAGE 1: Attempt $10.15
        print(f"⚡ {strategy} ATTEMPT 1: {pair} | RSI: {rsi:.2f} | STAKE: ${self.min_stake}")
        try:
             await self.exchange.create_order(
                 symbol=pair, type='market', side='buy', amount=None,
                 params={'quoteOrderQty': self.min_stake}
             )
             print(f"✅ SUCCESS: {pair} BOUGHT AT ${self.min_stake}")
             return
        except Exception as e:
             print(f"⚠️ ATTEMPT 1 KNOCKED BACK: {e}")

        # STAGE 2: Fallback to $10.20
        print(f"⚡ {strategy} ATTEMPT 2: {pair} | STAKE: ${self.fallback_stake}")
        try:
             await self.exchange.create_order(
                 symbol=pair, type='market', side='buy', amount=None,
                 params={'quoteOrderQty': self.fallback_stake}
             )
             print(f"✅ SUCCESS: {pair} BOUGHT AT ${self.fallback_stake}")
        except Exception as e:
             print(f"❌ ATTEMPT 2 FAILED: {e}")

    async def start_loop(self):
        print("🔥 VORTEX v4.2.4: TACTICAL ESCALATION LIVE")
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
                        
                        await asyncio.sleep(0.5)
                    except: continue

                self.slot_status = current_scan_data
                await asyncio.sleep(10)
            except Exception as e:
                print(f"Loop Error: {e}")
                await asyncio.sleep(10)