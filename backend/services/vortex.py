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
        self.starting_capital = 94.50
        self.base_stake = 10.50
        self.initial_slots = 9
        self.max_slots = 35
        
        # --- STATE ---
        self.wallet_balance = 0.0
        self.total_profit = 0.0
        self.next_slot_price = 0.0
        self.active_slots = self.initial_slots
        self.current_stake = self.base_stake
        self.held_coins = {}
        self.slot_status = []
        
        # --- KEYS ---
        api_key = os.getenv('BINANCE_API_KEY')
        secret_key = os.getenv('BINANCE_SECRET') 
        if not secret_key: secret_key = os.getenv('BINANCE_SECRET_KEY')

        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot', 'adjustForTimeDifference': True}
        })
        self.exchange.set_sandbox_mode(False)

    def get_slot_strategy(self, slot_id):
        # --- THE STRATEGY MAP ---
        # 1-14:   FAST VOLATILITY (Harvesters)
        # 15-20:  STANDARD (Snipers)
        # 21-25:  FAST VOLATILITY (Harvesters)
        # 26-31:  STANDARD (Snipers)
        # 32-35:  FAST VOLATILITY (Harvesters)
        
        if 1 <= slot_id <= 14: return 'HARVESTER'
        if 15 <= slot_id <= 20: return 'STANDARD'
        if 21 <= slot_id <= 25: return 'HARVESTER'
        if 26 <= slot_id <= 31: return 'STANDARD'
        if 32 <= slot_id <= 35: return 'HARVESTER'
        return 'HARVESTER' # Default fallback

    async def update_telemetry(self):
        # 1. PROFIT CALC
        if self.wallet_balance > 0:
            self.total_profit = self.wallet_balance - self.starting_capital
        
        # 2. SLOT GROWTH (Add 1 slot per $10.50 profit)
        earned_slots = int(max(0, self.total_profit) / 10.50)
        potential_slots = self.initial_slots + earned_slots
        
        # 3. END GAME (Compounding Stake)
        if potential_slots > self.max_slots:
            self.active_slots = self.max_slots
            # Spread extra profit into stake size
            # e.g. If we have profit for 40 slots, the extra 5 slots worth ($52.50) 
            # gets divided across the active 35 slots.
            surplus_profit = (potential_slots - self.max_slots) * 10.50
            self.current_stake = self.base_stake + (surplus_profit / self.max_slots)
        else:
            self.active_slots = potential_slots
            self.current_stake = self.base_stake

        # Next goal calculation
        next_threshold = (earned_slots + 1) * 10.50
        self.next_slot_price = max(0, next_threshold - self.total_profit)

    async def fetch_portfolio(self):
        try:
            balance = await self.exchange.fetch_balance()
            self.wallet_balance = balance['total'].get('USDT', 0)
            holdings = {}
            for coin, amount in balance['total'].items():
                if amount > 0 and coin != 'USDT':
                    holdings[coin] = f"{amount:.4f}"
            self.held_coins = holdings
        except: pass

    async def fetch_top_pairs(self):
        # MIX OF HIGH VOLATILITY & STABLE VOLUME
        return [
            'SOL/USDT', 'XRP/USDT', 'PEPE/USDT', 'DOGE/USDT', 'BTC/USDT', 
            'ETH/USDT', 'ADA/USDT', 'BNB/USDT', 'TRX/USDT', 'SHIB/USDT',
            'SUI/USDT', 'APT/USDT', 'LTC/USDT', 'NEAR/USDT', 'AVAX/USDT'
        ]

    async def execute_trade(self, pair, strategy, rsi):
        # CHECK FUNDS
        if self.wallet_balance < self.current_stake:
            print(f"⚠️ {pair}: INSUFFICIENT FUNDS. Waiting for sale.")
            return

        print(f"⚡ {strategy} TRIGGER: {pair} | RSI: {rsi:.2f} | BUYING ${self.current_stake:.2f}...")
        
        # --- FIRE THE TRADE ---
        try:
             # REAL ORDER EXECUTION
             order = await self.exchange.create_market_buy_order(pair, self.current_stake)
             print(f"✅ BOUGHT {pair} at {order.get('price', 'Market Price')}")
        except Exception as e:
             print(f"❌ TRADE ERROR: {e}")

    async def start_loop(self):
        print("🔥 VORTEX v4.2: UNLEASHED")
        
        try:
            while True:
                try:
                    await self.fetch_portfolio()
                    await self.update_telemetry()
                    
                    market_pairs = await self.fetch_top_pairs()
                    current_scan_data = []
                    
                    print(f"💰 WALLET: {self.wallet_balance:.2f} | 🎰 SLOTS: {self.active_slots} | 💵 STAKE: ${self.current_stake:.2f}")

                    for i in range(1, self.active_slots + 1):
                        strategy = self.get_slot_strategy(i)
                        pair = market_pairs[(i - 1) % len(market_pairs)]
                        
                        try:
                            # 1. FETCH CANDLES (1 Minute)
                            ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='1m', limit=50)
                            df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
                            df['rsi'] = ta.rsi(df['c'], length=14)
                            rsi = df['rsi'].iloc[-1]
                            
                            # 2. CHECK TRIGGERS
                            triggered = False
                            
                            if strategy == 'HARVESTER':
                                # AGGRESSIVE: Buy dips in uptrends (RSI < 55)
                                if rsi < 55: triggered = True
                            
                            elif strategy == 'STANDARD':
                                # CONSERVATIVE: Buy deep dips (RSI < 40)
                                if rsi < 40: triggered = True
                            
                            # 3. REPORTING
                            status_msg = "🔴 BUY" if triggered else "HUNTING"
                            print(f"Slot {i:02d} | {strategy[0]} | {pair:<10} | RSI: {rsi:.2f} {status_msg}")
                            
                            current_scan_data.append({
                                "slot": i, "pair": pair, "strategy": strategy, "rsi": f"{rsi:.2f}", "status": status_msg
                            })

                            if triggered:
                                await self.execute_trade(pair, strategy, rsi)

                        except Exception as e:
                            print(f"Slot {i} Error: {e}")
                        
                        # RATE LIMIT: 0.5s pause per slot (Safe for 35 slots)
                        await asyncio.sleep(0.5)

                    self.slot_status = current_scan_data
                    
                    # COOLDOWN: 10s between full cycles
                    await asyncio.sleep(10)

                except Exception as e:
                    print(f"⚠️ LOOP ERROR: {e}")
                    await asyncio.sleep(10)
        finally:
            await self.exchange.close()