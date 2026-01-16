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
        self.base_stake = 10.50
        self.initial_slots = 9
        self.max_slots = 35
        self.initial_balance = 0.0 # Will set on first run
        
        # --- STATE ---
        self.wallet_balance = 0.0
        self.active_slots = self.initial_slots
        self.current_stake = self.base_stake
        self.active_trades = [] # Track open orders
        
        # --- KEYS ---
        api_key = os.getenv('BINANCE_API_KEY')
        secret_key = os.getenv('BINANCE_SECRET') 
        if not secret_key: secret_key = os.getenv('BINANCE_SECRET_KEY')

        # --- CONNECT (SAFE MODE) ---
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True, # CRITICAL FOR 35 SLOTS
            'options': {'defaultType': 'spot', 'adjustForTimeDifference': True}
        })
        self.exchange.set_sandbox_mode(False)

    def get_slot_strategy(self, slot_id):
        # MAPPING RULES
        # 1-14: Volatility
        # 15-20: Standard
        # 21-25: Volatility
        # 26-31: Standard
        # 32-35: Volatility
        if 1 <= slot_id <= 14: return 'VOLATILE'
        if 15 <= slot_id <= 20: return 'STANDARD'
        if 21 <= slot_id <= 25: return 'VOLATILE'
        if 26 <= slot_id <= 31: return 'STANDARD'
        if 32 <= slot_id <= 35: return 'VOLATILE'
        return 'VOLATILE' # Fallback

    async def calculate_growth(self):
        # 1. GET PROFIT
        if self.initial_balance == 0: 
            self.initial_balance = self.wallet_balance # Set baseline
            return

        profit = self.wallet_balance - self.initial_balance
        
        # 2. CALCULATE SLOTS
        # Start with 9, add 1 for every $10.50 profit
        earned_slots = int(profit / 10.50)
        new_slot_count = self.initial_slots + earned_slots
        
        # 3. APPLY LIMITS (The "End Game" Logic)
        if new_slot_count > self.max_slots:
            self.active_slots = self.max_slots
            # SURPLUS PROFIT RAISES STAKE
            surplus_slots = new_slot_count - self.max_slots
            # e.g. If we have profit for 36 slots, increase stake by small increment
            self.current_stake = self.base_stake + (surplus_slots * 0.50) 
        else:
            self.active_slots = new_slot_count
            self.current_stake = self.base_stake

    async def fetch_top_pairs(self):
        # API OPTIMIZATION: Get all tickers in 1 call to avoid banning
        try:
            tickers = await self.exchange.fetch_tickers()
            # Filter for USDT pairs with high volume (>5M) to ensure liquidity
            pairs = []
            for symbol, data in tickers.items():
                if '/USDT' in symbol and data['quoteVolume'] > 5000000:
                    # Exclude stablecoins
                    if not any(x in symbol for x in ['USDC', 'FDUSD', 'TUSD', 'DAI']):
                        pairs.append(symbol)
            return pairs[:50] # Top 50 candidates
        except:
            return ['SOL/USDT', 'XRP/USDT', 'PEPE/USDT', 'DOGE/USDT', 'BTC/USDT', 'ETH/USDT']

    async def start_loop(self):
        print("🔥 VORTEX v3.0: MASSIVE SCALING ENGINE LIVE")
        
        try:
            while True:
                try:
                    # --- 1. REFRESH WALLET & GROWTH ---
                    balance = await self.exchange.fetch_balance()
                    self.wallet_balance = balance['total'].get('USDT', 0)
                    await self.calculate_growth()
                    
                    print(f"💰 WALLET: {self.wallet_balance:.2f} USDT | 🎰 SLOTS: {self.active_slots} | 💵 STAKE: ${self.current_stake:.2f}")

                    # --- 2. GET TARGETS ---
                    market_pairs = await self.fetch_top_pairs()
                    
                    # --- 3. SCAN SLOTS ---
                    # We process slots sequentially but check rate limits
                    for i in range(1, self.active_slots + 1):
                        strategy_type = self.get_slot_strategy(i)
                        
                        # Assign a pair to this slot (Round Robin style for now)
                        # Slot 1 gets Pair 1, Slot 2 gets Pair 2, etc.
                        pair_idx = (i - 1) % len(market_pairs)
                        pair = market_pairs[pair_idx]
                        
                        # LOGIC BRANCH
                        if strategy_type == 'VOLATILE':
                            # Fast Chaser: Needs RSI < 30
                            # We simulate the check to save API calls in this display loop
                            # In real execution, we would fetchOHLCV here.
                            pass 
                            
                        # Rate Limit Protect (Sleep small amount between slots)
                        # But since we aren't trading real orders yet in this loop demo:
                        pass
                        
                    print(f"🔍 SCANNING {len(market_pairs)} PAIRS across {self.active_slots} SLOTS...")
                    
                    # Wait 10s between full cycles to respect Binance Weight
                    await asyncio.sleep(10)

                except Exception as e:
                    print(f"⚠️ ERROR: {e}")
                    await asyncio.sleep(10)
        finally:
            await self.exchange.close()