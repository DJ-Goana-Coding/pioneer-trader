import os
import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import pandas_ta as ta
from dotenv import load_dotenv

load_dotenv()

class VortexEngine:
    def __init__(self):
        # --- CONFIGURATION ---
        self.starting_capital = 94.50  # FIXED START FOR PROFIT CALC
        self.base_stake = 10.50
        self.initial_slots = 9
        self.max_slots = 35
        
        # --- LIVE DATA (For HUD) ---
        self.wallet_balance = 0.0
        self.total_profit = 0.0
        self.next_slot_price = 0.0
        self.active_slots = self.initial_slots
        self.current_stake = self.base_stake
        self.held_coins = {}   # Portfolio Dictionary
        self.slot_status = []  # Live Slot Details
        
        # --- KEYS ---
        api_key = os.getenv('BINANCE_API_KEY')
        secret_key = os.getenv('BINANCE_SECRET') 
        if not secret_key: secret_key = os.getenv('BINANCE_SECRET_KEY')

        # --- CONNECT ---
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot', 'adjustForTimeDifference': True}
        })
        self.exchange.set_sandbox_mode(False)

    def get_slot_strategy(self, slot_id):
        # STRATEGY MAP
        if 1 <= slot_id <= 14: return 'VOLATILE'  # RSI < 30
        if 15 <= slot_id <= 20: return 'STANDARD' # RSI < 40
        if 21 <= slot_id <= 25: return 'VOLATILE'
        if 26 <= slot_id <= 31: return 'STANDARD'
        if 32 <= slot_id <= 35: return 'VOLATILE'
        return 'VOLATILE'

    async def update_telemetry(self):
        # 1. CALCULATE PROFIT
        if self.wallet_balance > 0:
            self.total_profit = self.wallet_balance - self.starting_capital
        
        # 2. CALCULATE SLOTS & NEXT GOAL
        # Logic: 9 base slots. Add 1 slot for every $10.50 profit.
        earned_slots = int(max(0, self.total_profit) / 10.50)
        self.active_slots = min(self.initial_slots + earned_slots, self.max_slots)
        
        # How much $ needed for the NEXT slot?
        next_threshold = (earned_slots + 1) * 10.50
        self.next_slot_price = max(0, next_threshold - self.total_profit)

    async def fetch_portfolio(self):
        # GET HELD COINS
        try:
            balance = await self.exchange.fetch_balance()
            self.wallet_balance = balance['total'].get('USDT', 0)
            
            # Save non-zero coins for the HUD
            holdings = {}
            for coin, amount in balance['total'].items():
                if amount > 0 and coin != 'USDT':
                    holdings[coin] = f"{amount:.4f}"
            self.held_coins = holdings
        except Exception as e:
            print(f"⚠️ PORTFOLIO ERROR: {e}")

    async def fetch_top_pairs(self):
        # GET VOLATILE PAIRS (SIMPLIFIED FOR SPEED)
        # In full prod, this scans all tickers. For now, we use a robust list.
        return [
            'SOL/USDT', 'XRP/USDT', 'PEPE/USDT', 'DOGE/USDT', 'BTC/USDT', 
            'ETH/USDT', 'ADA/USDT', 'BNB/USDT', 'TRX/USDT', 'SHIB/USDT',
            'AVAX/USDT', 'LINK/USDT', 'DOT/USDT', 'MATIC/USDT', 'LTC/USDT'
        ]

    async def execute_trade(self, pair, strategy, rsi):
        # CHECK FUNDS
        if self.wallet_balance < self.current_stake:
            print(f"⚠️ {pair}: INSUFFICIENT FUNDS ({self.wallet_balance} < {self.current_stake})")
            return

        print(f"⚡ BUY SIGNAL: {pair} | {strategy} | RSI: {rsi:.2f}")
        # UNCOMMENT TO ENABLE REAL TRADING:
        # await self.exchange.create_market_buy_order(pair, self.current_stake)

    async def start_loop(self):
        print("🔥 VORTEX v4.0: ENGINE LIVE")
        
        try:
            while True:
                try:
                    # 1. REFRESH DATA
                    await self.fetch_portfolio()
                    await self.update_telemetry()
                    
                    print(f"💰 WALLET: {self.wallet_balance:.2f} | 📈 PROFIT: {self.total_profit:.2f} | 🎰 SLOTS: {self.active_slots}")

                    # 2. GET PAIRS
                    market_pairs = await self.fetch_top_pairs()
                    current_scan_data = [] # Reset for API
                    
                    # 3. SCAN SLOTS
                    for i in range(1, self.active_slots + 1):
                        strategy = self.get_slot_strategy(i)
                        pair = market_pairs[(i - 1) % len(market_pairs)]
                        
                        # FETCH RSI
                        try:
                            ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='1m', limit=50)
                            df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
                            df['rsi'] = ta.rsi(df['c'], length=14)
                            rsi = df['rsi'].iloc[-1]
                            
                            # LOGIC
                            triggered = False
                            if strategy == 'VOLATILE' and rsi < 30: triggered = True
                            if strategy == 'STANDARD' and rsi < 40: triggered = True
                            
                            status_msg = "🔴 BUY" if triggered else "SCANNING"
                            print(f"Slot {i:02d} | {strategy[0]} | {pair:<10} | RSI: {rsi:.2f} {status_msg}")
                            
                            # STORE DATA FOR HUD
                            current_scan_data.append({
                                "slot": i, "pair": pair, "strategy": strategy, "rsi": f"{rsi:.2f}", "status": status_msg
                            })

                            if triggered:
                                await self.execute_trade(pair, strategy, rsi)

                        except Exception as e:
                            print(f"Slot {i} Error: {e}")
                        
                        await asyncio.sleep(0.5) # Rate Limit

                    # UPDATE HUD DATA
                    self.slot_status = current_scan_data
                    
                    await asyncio.sleep(10)

                except Exception as e:
                    print(f"⚠️ LOOP ERROR: {e}")
                    await asyncio.sleep(10)
        finally:
            await self.exchange.close()