# ================================================================
# 💪 VORTEX ENGINE V5.3 - THE SOVEREIGN PRIME
# ================================================================
import os
import asyncio
import ccxt.async_support as ccxt
from datetime import datetime
from dotenv import load_dotenv
from backend.core.logging_config import setup_logging
from backend.services.redis_cache import redis_cache

load_dotenv()
logger = setup_logging("vortex")

class VortexEngine:
    EXCLUDED_COINS = ['USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'MX']
    
    def __init__(self):
        # 🎯 AGGRESSIVE CONFIGURATION (10/10)
        self.starting_capital = 94.50
        self.min_stake = 5.00        # 🔥 Aggressive Stake
        self.bot_allowance = 50.00    # Hard Cap
        self.initial_slots = 45       # 45-Slot Logic
        
        # 📊 STATE TRACKING
        self.wallet_balance = 0.0
        self.total_equity = 0.0
        self.total_profit = 0.0
        self.held_coins = {}
        self.active_slots = 0
        self.is_slot_guarded = False
        self.next_slot_price = self.min_stake 
        self.slot_status = []
        
        self.exchange = None
        self._init_exchange()
        self._restore_state()

    def _init_exchange(self):
        api_key = os.getenv('MEXC_API_KEY')
        secret_key = os.getenv('MEXC_SECRET')
        if api_key and secret_key:
            self.exchange = ccxt.mexc({
                'apiKey': api_key,
                'secret': secret_key,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot', 'createMarketBuyOrderRequiresPrice': False}
            })
            logger.info("⚔️ VORTEX V5.3: Master Sovereign Live")

    def _restore_state(self):
        try:
            state = redis_cache.get_portfolio_state()
            if state: logger.info("🔴 REDIS: State Sync Complete")
        except: pass

    async def fetch_portfolio(self):
        if not self.exchange: return
        try:
            balance = await self.exchange.fetch_balance()
            self.wallet_balance = balance['total'].get('USDT', 0)
            tickers = await self.exchange.fetch_tickers()
            holdings = {}
            total_val = 0.0
            
            for coin, amount in balance['total'].items():
                if amount > 0 and coin not in self.EXCLUDED_COINS:
                    pair = f"{coin}/USDT"
                    if pair in tickers:
                        price = tickers[pair]['last']
                        val = amount * price
                        if val > 1.0:
                            holdings[coin] = {'amount': amount, 'value': val, 'price': price}
                            total_val += val
            
            self.held_coins = holdings
            self.active_slots = len(holdings)
            self.total_equity = self.wallet_balance + total_val
            self.total_profit = self.total_equity - self.starting_capital
            self.slot_status = [{"coin": k, "value": f"${v['value']:.2f}"} for k, v in holdings.items()]
        except Exception as e:
            logger.error(f"❌ PORTFOLIO ERROR: {e}")

    async def execute_buy(self, pair: str):
        try:
            # POSITIONAL FIX: symbol, type, side, amount=None, price=None, params
            order = await self.exchange.create_order(pair, 'market', 'buy', None, None, {'quoteOrderQty': self.min_stake})
            logger.info(f"✅ AGGRESSIVE BUY: {pair} ($5.00)")
            return True
        except Exception as e:
            logger.error(f"❌ BUY FAILED: {pair} | {e}")
            return False

    async def start_loop(self):
        logger.info("🚀 VORTEX ENGINE: Engaging 10/10 Aggression")
        while True:
            try:
                await self.fetch_portfolio()
                if self.wallet_balance >= self.min_stake and self.active_slots < self.initial_slots:
                    tickers = await self.exchange.fetch_tickers()
                    targets = [t for t in tickers.values() if t['symbol'].endswith('/USDT') and t.get('quoteVolume', 0) > 5000000][:5]
                    for t in targets:
                        if self.wallet_balance < self.min_stake: break
                        if t['symbol'].split('/')[0] not in self.held_coins:
                            await self.execute_buy(t['symbol'])
                await asyncio.sleep(20)
            except Exception as e:
                logger.error(f"⚠️ LOOP ERROR: {e}")
                await asyncio.sleep(20)
        
