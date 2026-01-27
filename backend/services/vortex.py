# ================================================================
# 🔥 VORTEX V6.5 - THE BERSERKER (1S BEAT + 103 SLOTS + TRAILING)
# ================================================================
import os, asyncio, ccxt.async_support as ccxt
from datetime import datetime
from backend.core.logging_config import setup_logging

logger = setup_logging("vortex")

class VortexEngine:
    def __init__(self):
        self.scout_stake = 3.50    
        self.soldier_stake = 5.00  
        self.initial_slots = 103   # 🛡️ EXPANDED SLOTS
        self.aggression = 15       
        self.target_profit_usdt = 0.20 # 💰 THE 20-CENT SNIPE TARGET
        self.trail_percent = 0.005    # 🎢 0.5% Trailing Stop to "Ride the Run"
        
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
                'rateLimit': 50, # ⚡ High-frequency polling
                'options': {'defaultType': 'spot'}
            })
            logger.info("⚔️ V6.5 BERSERKER ENGAGED: 1s Pulse | 103 Slots")

    async def fetch_portfolio(self):
        if not self.exchange: return
        try:
            balance = await self.exchange.fetch_balance()
            self.wallet_balance = float(balance['total'].get('USDT', 0))
            tickers = await self.exchange.fetch_tickers()
            
            # 🕵️ Update Held Coins & Trailing Logic
            for coin, amount in balance['total'].items():
                pair = f"{coin}/USDT"
                if amount > 0 and pair in tickers:
                    last_price = tickers[pair]['last']
                    if coin not in self.held_coins:
                        self.held_coins[coin] = {'buy_price': last_price, 'max_price': last_price}
                    
                    # Update "High Water Mark" for Trailing
                    if last_price > self.held_coins[coin]['max_price']:
                        self.held_coins[coin]['max_price'] = last_price
                    
                    # 🚦 EXIT LOGIC: 20c Profit + Trailing Drop
                    profit_usdt = (last_price - self.held_coins[coin]['buy_price']) * amount
                    trail_trigger = self.held_coins[coin]['max_price'] * (1 - self.trail_percent)
                    
                    if profit_usdt >= self.target_profit_usdt:
                        if last_price <= trail_trigger: # Price dropped from peak
                            await self.execute_exit(pair, amount, profit_usdt)
        except Exception as e: logger.debug(f"Sync: {e}")

    async def execute_exit(self, pair, amount, profit):
        try:
            await self.exchange.create_market_sell_order(pair, amount)
            msg = f"💰 SNIPE SECURED: {pair} (+${profit:.2f})"
            self._log_trade(msg)
            if pair.split('/')[0] in self.held_coins:
                del self.held_coins[pair.split('/')[0]]
        except Exception as e: logger.error(f"Exit Fail: {e}")

    async def execute_chameleon_buy(self, pair: str):
        try:
            # 🎯 1-Second Scout Attempt
            await self.exchange.create_order(pair, 'market', 'buy', None, None, {'quoteOrderQty': self.scout_stake})
            self._log_trade(f"🔥 BERSERKER SCOUT: {pair} ($3.50)")
        except Exception as e:
            if "minimum" in ("notional", str(e).lower()):
                try:
                    await self.exchange.create_order(pair, 'market', 'buy', None, None, {'quoteOrderQty': self.soldier_stake})
                    self._log_trade(f"🛡️ BERSERKER SOLDIER: {pair} ($5.00)")
                except: pass

    def _log_trade(self, msg):
        now = datetime.now().strftime("%H:%M:%S")
        logger.info(msg)
        self.last_trades.insert(0, f"[{now}] {msg}")
        self.last_trades = self.last_trades[:10]

    async def start_loop(self):
        while True:
            try:
                await self.fetch_portfolio()
                if self.wallet_balance >= self.scout_stake and len(self.held_coins) < self.initial_slots:
                    tickers = await self.exchange.fetch_tickers()
                    # 🕵️ Sniper Logic: Volume > 3M to find the "active runners"
                    targets = [t for t in tickers.values() if t['symbol'].endswith('/USDT') and t.get('quoteVolume', 0) > 3000000]
                    for t in targets[:self.aggression]:
                        if t['symbol'].split('/')[0] not in self.held_coins:
                            await self.execute_chameleon_buy(t['symbol'])
                            break 
                await asyncio.sleep(1) # ⚡ THE 1-SECOND PULSE
            except: await asyncio.sleep(1)
                
