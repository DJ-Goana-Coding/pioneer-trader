# ================================================================
# 💪 VORTEX ENGINE V5.0 - THE MASTER SOVEREIGN
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
        # 🎯 SLOT CONFIGURATION
        self.starting_capital = 94.50
        self.min_stake = 10.50
        self.min_trade_floor = 5.50
        self.initial_slots = 15
        
        # 📊 STATE TRACKING
        self.wallet_balance = 0.0
        self.total_equity = 0.0
        self.total_profit = 0.0
        self.held_coins = {}
        self.peak_prices = {}
        self.active_slots = 0
        self.is_slot_guarded = False
        self.next_slot_price = self.min_stake 
        
        self._restore_state_from_redis()
        
        api_key = os.getenv('MEXC_API_KEY')
        secret_key = os.getenv('MEXC_SECRET')
        
        if not api_key or not secret_key:
            logger.warning("⚠️ VORTEX: Keys missing, running in BLIND MODE")
            self.exchange = None
        else:
            self.exchange = ccxt.mexc({
                'apiKey': api_key,
                'secret': secret_key,
                'enableRateLimit': True,
                'options': { 'defaultType': 'spot', 'createMarketBuyOrderRequiresPrice': False }
            })
            logger.info("⚔️ VORTEX V5.0: MASTER SOVEREIGN Ignition Success")

    def _restore_state_from_redis(self):
        try:
            state = redis_cache.get_portfolio_state()
            if state:
                self.peak_prices = redis_cache.get_all_peaks()
                logger.info(f"🔴 REDIS: Restored {len(self.peak_prices)} peaks")
        except: pass

    def _persist_state_to_redis(self):
        redis_cache.save_portfolio_state({
            'wallet_balance': self.wallet_balance,
            'total_equity': self.total_equity,
            'total_profit': self.total_profit,
            'active_slots': self.active_slots,
            'held_coins': self.held_coins
        })

    async def fetch_portfolio(self):
        if not self.exchange: return
        try:
            balance = await self.exchange.fetch_balance()
            self.wallet_balance = balance['total'].get('USDT', 0)
            tickers = await self.exchange.fetch_tickers()
            holdings = {}
            total_holdings_value = 0.0
            
            for coin, amount in balance['total'].items():
                if amount > 0 and coin not in self.EXCLUDED_COINS:
                    pair = f"{coin}/USDT"
                    if pair in tickers:
                        price = tickers[pair]['last']
                        val = amount * price
                        if val > 1.0:
                            holdings[coin] = {'amount': round(amount, 6), 'value': round(val, 2), 'price': price}
                            total_holdings_value += val
            
            self.held_coins = holdings
            self.active_slots = len(holdings)
            self.total_equity = self.wallet_balance + total_holdings_value
            self.total_profit = self.total_equity - self.starting_capital
            self._persist_state_to_redis()
        except Exception as e:
            logger.error(f"❌ PORTFOLIO FETCH ERROR: {e}")

    async def execute_buy(self, pair: str) -> bool:
        """HARDENED: Guaranteed 4-point positional handshake"""
        if not self.exchange: return False
        try:
            order = await self.exchange.create_order(
                pair,       # 1. symbol
                'market',   # 2. type
                'buy',      # 3. side
                None,       # 4. amount (THE CRITICAL FIX)
                None,       # 5. price
                {'quoteOrderQty': self.min_stake} # 6. params
            )
            logger.info(f"✅ BUY SUCCESS: {pair} | ID: {order.get('id')}")
            return True
        except Exception as e:
            logger.error(f"❌ BUY FAILED: {pair} | REASON: {e}")
            return False

    async def start_loop(self):
        logger.info("🔍 VORTEX V5.0: SOVEREIGN ACTIVE")
        while True:
            try:
                await self.fetch_portfolio()
                now = datetime.now().strftime('%H:%M:%S')
                print(f"--- [VORTEX {now}] Wallet: ${self.wallet_balance:.2f} | Equity: ${self.total_equity:.2f} ---")

                if self.wallet_balance < self.min_stake:
                    logger.warning("🛡️ SLOT GUARD: Insufficient funds")
                    await asyncio.sleep(20); continue

                tickers = await self.exchange.fetch_tickers()
                targets = [
                    t for t in tickers.values() 
                    if t['symbol'].endswith('/USDT') 
                    and t.get('quoteVolume', 0) > 10000000
                    and t['symbol'].split('/')[0] not in self.held_coins
                    and t['symbol'].split('/')[0] not in self.EXCLUDED_COINS
                ][:5]

                for t in targets:
                    if self.wallet_balance < self.min_stake: break
                    await self.execute_buy(t['symbol'])
                
                await asyncio.sleep(20)
            except Exception as e:
                logger.error(f"⚠️ MAIN ERROR: {e}")
                await asyncio.sleep(20)

    async def shutdown(self):
        if self.exchange:
            await self.exchange.close()
            logger.info("🔌 VORTEX: Connection closed")
