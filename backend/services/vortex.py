# ================================================================
# 💪 VORTEX V6.2 - THE SOVEREIGN SCALPER (2S BEAT + SCOUT/SOLDIER)
# ================================================================
import os, asyncio, ccxt.async_support as ccxt
from datetime import datetime
from backend.core.logging_config import setup_logging

logger = setup_logging("vortex")

class VortexEngine:
    def __init__(self):
        self.scout_stake = 3.50    
        self.soldier_stake = 5.00  
        self.initial_slots = 100   
        self.aggression = 10       
        
        self.wallet_balance = 0.0
        self.held_coins = {}
        self.futures_positions = []
        self.last_trades = []      

        self.exchange = None
        self._init_exchange()

    def _init_exchange(self):
        keys = {'apiKey': os.getenv('MEXC_API_KEY'), 'secret': os.getenv('MEXC_SECRET')}
        if keys['apiKey']:
            self.exchange = ccxt.mexc({**keys, 'enableRateLimit': True, 'options': {'defaultType': 'spot'}})
            logger.info("⚔️ V6.2 SOVEREIGN: 2s Scout/Soldier Engaged")

    def _safe_float(self, val):
        try: return float(val) if val is not None else 0.0
        except: return 0.0

    async def fetch_portfolio(self):
        if not self.exchange: return
        try:
            balance = await self.exchange.fetch_balance()
            self.wallet_balance = self._safe_float(balance['total'].get('USDT', 0))
            
            # Silent Watch for the BTC 60x Long
            try:
                pos = await self.exchange.fetch_positions(params={'type': 'swap'})
                self.futures_positions = [p for p in pos if self._safe_float(p.get('contracts', 0)) > 0]
            except: pass 

            tickers = await self.exchange.fetch_tickers()
            self.held_coins = {c: {'val': a * tickers[f"{c}/USDT"]['last'], 'price': tickers[f"{c}/USDT"]['last']} 
                               for c, a in balance['total'].items() if a > 0 and f"{c}/USDT" in tickers}
        except Exception as e: logger.debug(f"Sync: {e}")

    async def execute_chameleon_buy(self, pair: str):
        try:
            # Attempt 1: Scout ($3.50)
            await self.exchange.create_order(pair, 'market', 'buy', None, None, {'quoteOrderQty': self.scout_stake})
            self._log_trade(f"🏃 SCOUT BUY: {pair} ($3.50)")
        except Exception as e:
            if "minimum" in str(e).lower() or "notional" in str(e).lower():
                try:
                    # Attempt 2: Soldier ($5.00)
                    await self.exchange.create_order(pair, 'market', 'buy', None, None, {'quoteOrderQty': self.soldier_stake})
                    self._log_trade(f"🛡️ SOLDIER BUY: {pair} ($5.00)")
                except: pass

    def _log_trade(self, msg):
        now = datetime.now().strftime("%H:%M:%S")
        logger.info(msg)
        self.last_trades.insert(0, f"[{now}] {msg}")
        self.last_trades = self.last_trades[:8]

    async def start_loop(self):
        while True:
            try:
                await self.fetch_portfolio()
                if self.wallet_balance >= self.scout_stake and len(self.held_coins) < self.initial_slots:
                    tickers = await self.exchange.fetch_tickers()
                    targets = [t for t in tickers.values() if t['symbol'].endswith('/USDT') and t.get('quoteVolume', 0) > 8000000]
                    for t in targets[:self.aggression]:
                        if t['symbol'].split('/')[0] not in self.held_coins:
                            await self.execute_chameleon_buy(t['symbol'])
                            break 
                await asyncio.sleep(2) # ⚡ 2 SECOND HEARTBEAT
            except Exception as e:
                await asyncio.sleep(2)
                    
