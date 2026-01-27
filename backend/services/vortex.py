# ================================================================
# 🔥 VORTEX V6.5 - THE BERSERKER (1S PULSE + RAPID FIRE EXITS)
# ================================================================
import os, asyncio, ccxt.async_support as ccxt
from datetime import datetime
from backend.core.logging_config import setup_logging

logger = setup_logging("vortex")

class VortexEngine:
    def __init__(self):
        # ⚔️ SCOUT & SOLDIER STAKES
        self.scout_stake = 3.50    
        self.soldier_stake = 5.00  
        
        # 🛡️ FLEET CONFIG
        self.initial_slots = 103   # Max capacity
        self.aggression = 15       # Scan intensity
        
        # ⚡ RAPID FIRE TUNING (POPCORN MODE)
        self.target_profit_usdt = 0.07  # 🎯 7 CENTS TARGET (approx 2% of $3.50)
        self.trail_percent = 0.002      # 🎢 0.2% TRAIL (Tight Snap)
        
        self.wallet_balance = 0.0
        self.held_coins = {} # Format: {symbol: {'buy_price': x, 'max_price': x}}
        self.last_trades = []      

        self.exchange = None
        self._init_exchange()

    def _init_exchange(self):
        keys = {'apiKey': os.getenv('MEXC_API_KEY'), 'secret': os.getenv('MEXC_SECRET')}
        if keys['apiKey']:
            self.exchange = ccxt.mexc({
                **keys, 
                'enableRateLimit': True, 
                'rateLimit': 50, # ⚡ High-frequency polling (50ms)
                'options': {'defaultType': 'spot'}
            })
            logger.info("⚔️ V6.5 BERSERKER ENGAGED: 1s Pulse | 103 Slots | 7c Target")

    def _safe_float(self, val):
        try: return float(val) if val is not None else 0.0
        except: return 0.0

    async def fetch_portfolio(self):
        if not self.exchange: return
        try:
            balance = await self.exchange.fetch_balance()
            self.wallet_balance = self._safe_float(balance['total'].get('USDT', 0))
            tickers = await self.exchange.fetch_tickers()
            
            # 🕵️ Update Held Coins & Trailing Logic
            for coin, amount in balance['total'].items():
                pair = f"{coin}/USDT"
                if amount > 0 and pair in tickers:
                    last_price = tickers[pair]['last']
                    
                    # Initialize tracking if new
                    if coin not in self.held_coins:
                        self.held_coins[coin] = {'buy_price': last_price, 'max_price': last_price}
                    
                    # Update "High Water Mark" for Trailing
                    if last_price > self.held_coins[coin]['max_price']:
                        self.held_coins[coin]['max_price'] = last_price
                    
                    # 🚦 EXIT LOGIC: 7c Profit + 0.2% Drop
                    # 1. Calculate Profit in USDT
                    profit_usdt = (last_price - self.held_coins[coin]['buy_price']) * amount
                    
                    # 2. Calculate Trailing Stop Price (Peak - 0.2%)
                    trail_trigger = self.held_coins[coin]['max_price'] * (1 - self.trail_percent)
                    
                    # 3. Trigger Check
                    if profit_usdt >= self.target_profit_usdt:
                        if last_price <= trail_trigger: # Price dropped from peak
                            await self.execute_exit(pair, amount, profit_usdt)
                            
        except Exception as e: logger.debug(f"Sync: {e}")

    async def execute_exit(self, pair, amount, profit):
        try:
            await self.exchange.create_market_sell_order(pair, amount)
            msg = f"💰 SNIPE SECURED: {pair} (+${profit:.2f})"
            self._log_trade(msg)
            # Remove from tracking immediately to free up slot
            coin = pair.split('/')[0]
            if coin in self.held_coins:
                del self.held_coins[coin]
        except Exception as e: logger.error(f"Exit Fail: {e}")

    async def execute_chameleon_buy(self, pair: str):
        try:
            # 🎯 1-Second Scout Attempt ($3.50)
            await self.exchange.create_order(pair, 'market', 'buy', None, None, {'quoteOrderQty': self.scout_stake})
            self._log_trade(f"🔥 BERSERKER SCOUT: {pair} ($3.50)")
        except Exception as e:
            # If $3.50 is too small, pivot to Soldier ($5.00)
            if "minimum" in str(e).lower() or "notional" in str(e).lower():
                try:
                    await self.exchange.create_order(pair, 'market', 'buy', None, None, {'quoteOrderQty': self.soldier_stake})
                    self._log_trade(f"🛡️ BERSERKER SOLDIER: {pair} ($5.00)")
                except: pass

    def _log_trade(self, msg):
        now = datetime.now().strftime("%H:%M:%S")
        logger.info(msg)
        self.last_trades.insert(0, f"[{now}] {msg}")
        self.last_trades = self.last_trades[:12] # Keep last 12 lines for the UI

    async def start_loop(self):
        while True:
            try:
                await self.fetch_portfolio()
                # 🛡️ Check 103 slots capacity
                if self.wallet_balance >= self.scout_stake and len(self.held_coins) < self.initial_slots:
                    tickers = await self.exchange.fetch_tickers()
                    # 🕵️ Sniper Logic: Volume > 3M to find active runners
                    targets = [t for t in tickers.values() if t['symbol'].endswith('/USDT') and t.get('quoteVolume', 0) > 3000000]
                    for t in targets[:self.aggression]:
                        if t['symbol'].split('/')[0] not in self.held_coins:
                            await self.execute_chameleon_buy(t['symbol'])
                            break 
                await asyncio.sleep(1) # ⚡ THE 1-SECOND PULSE
            except: await asyncio.sleep(1)
    
