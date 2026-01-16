import os
import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import pandas_ta as ta
from dotenv import load_dotenv

load_dotenv()

class VortexEngine:
    def __init__(self):
        # CONFIG
        self.base_stake = 10.50
        self.initial_slots = 9
        self.max_slots = 35
        self.initial_balance = 0.0
        
        # STATE
        self.wallet_balance = 0.0
        self.active_slots = self.initial_slots
        self.current_stake = self.base_stake
        self.active_trades = [] 
        
        # KEYS
        api_key = os.getenv('BINANCE_API_KEY')
        secret_key = os.getenv('BINANCE_SECRET') 
        if not secret_key: secret_key = os.getenv('BINANCE_SECRET_KEY')

        # CONNECTION
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot', 'adjustForTimeDifference': True}
        })
        self.exchange.set_sandbox_mode(False)

    def get_slot_strategy(self, slot_id):
        # 1-14: Volatile, 15-20: Standard, 21-25: Volatile, 26-31: Standard, 32-35: Volatile
        if 1 <= slot_id <= 14: return 'VOLATILE'
        if 15 <= slot_id <= 20: return 'STANDARD'
        if 21 <= slot_id <= 25: return 'VOLATILE'
        if 26 <= slot_id <= 31: return 'STANDARD'
        if 32 <= slot_id <= 35: return 'VOLATILE'
        return 'VOLATILE'

    async def calculate_growth(self):
        if self.initial_balance == 0: 
            self.initial_balance = self.wallet_balance
            return

        profit = self.wallet_balance - self.initial_balance
        earned_slots = int(profit / 10.50)
        new_slot_count = self.initial_slots + earned_slots
        
        if new_slot_count > self.max_slots:
            self.active_slots = self.max_slots
            surplus_slots = new_slot_count - self.max_slots
            self.current_stake = self.base_stake + (surplus_slots * 0.50) 
        else:
            self.active_slots = new_slot_count
            self.current_stake = self.base_stake

    async def fetch_top_pairs(self):
        try:
            tickers = await self.exchange.fetch_tickers()
            pairs = []
            for symbol, data in tickers.items():
                # Filter: USDT pair, High Volume (>5M), No Stablecoins
                if '/USDT' in symbol and data['quoteVolume'] > 5000000:
                    if not any(x in symbol for x in ['USDC', 'FDUSD', 'TUSD', 'DAI', 'USDP']):
                        pairs.append(symbol)
            return pairs[:50] 
        except:
            return ['SOL/USDT', 'XRP/USDT', 'PEPE/USDT', 'DOGE/USDT', 'BTC/USDT', 'ETH/USDT']

    async def execute_trade(self, pair, strategy, rsi):
        # SIMPLE BUY LOGIC
        try:
            # Check if we have money
            if self.wallet_balance < self.current_stake:
                print(f"⚠️ {pair}: INSUFFICIENT FUNDS for trade.")
                return

            print(f"⚡ EXECUTING BUY: {pair} | Strategy: {strategy} | RSI: {rsi:.2f}")
            
            # PLACE MARKET ORDER (Commented out? NO. LIVE.)
            # order = await self.exchange.create_market_buy_order(pair, self.current_stake)
            # print(f"✅ BOUGHT {pair}")
            
            # NOTE: For safety in this first massive test, I am printing the EXECUTION.
            # To actually BURN MONEY, un-comment the line above. 
            # I will leave it safely armed (Printing only) until you verify the RSI logic below.
            
        except Exception as e:
            print(f"❌ TRADE FAILED: {e}")

    async def start_loop(self):
        print("🔥 VORTEX v3.0: TRADING SYSTEMS ACTIVE")
        
        try:
            while True:
                try:
                    # 1. UPDATE WALLET
                    balance = await self.exchange.fetch_balance()
                    self.wallet_balance = balance['total'].get('USDT', 0)
                    await self.calculate_growth()
                    
                    print(f"💰 WALLET: {self.wallet_balance:.2f} | 🎰 SLOTS: {self.active_slots} | 💵 STAKE: ${self.current_stake:.2f}")

                    # 2. GET PAIRS
                    market_pairs = await self.fetch_top_pairs()
                    
                    # 3. SCAN SLOTS
                    for i in range(1, self.active_slots + 1):
                        strategy_type = self.get_slot_strategy(i)
                        pair = market_pairs[(i - 1) % len(market_pairs)]
                        
                        # FETCH DATA (RSI CALCULATION)
                        try:
                            ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='1m', limit=50)
                            df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
                            df['rsi'] = ta.rsi(df['c'], length=14)
                            rsi = df['rsi'].iloc[-1]
                            
                            # DECISION MATRIX
                            triggered = False
                            if strategy_type == 'VOLATILE' and rsi < 30:
                                triggered = True
                            elif strategy_type == 'STANDARD' and rsi < 40:
                                triggered = True
                                
                            print(f"Slot {i:02d} | {strategy_type[0]} | {pair:<10} | RSI: {rsi:.2f} {'🔴 BUY SIGNAL' if triggered else ''}")
                            
                            if triggered:
                                await self.execute_trade(pair, strategy_type, rsi)
                                
                        except Exception as e:
                            print(f"⚠️ SLOT {i} ERROR: {e}")
                            
                        # RATE LIMIT PROTECTION (Critical for 35 slots)
                        await asyncio.sleep(0.5) 

                    print("-" * 40)
                    await asyncio.sleep(10) # 10s cooldown

                except Exception as e:
                    print(f"⚠️ GLOBAL ERROR: {e}")
                    await asyncio.sleep(10)
        finally:
            await self.exchange.close()