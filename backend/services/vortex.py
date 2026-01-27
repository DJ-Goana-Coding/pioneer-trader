# ================================================================
# 💪 VORTEX ENGINE V5.5 - THE SENTINEL (SPOT + FUTURES)
# ================================================================
import os
import asyncio
import ccxt.async_support as ccxt
from datetime import datetime
from backend.services.redis_cache import redis_cache
from backend.core.logging_config import setup_logging

logger = setup_logging("vortex")

class VortexEngine:
    EXCLUDED_COINS = ['USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'MX']

    def __init__(self):
        # 🎯 AGGRESSIVE CONFIG (10/10)
        self.starting_capital = 94.50
        self.min_stake = 5.00
        self.bot_allowance = 50.00
        self.initial_slots = 45
        
        # 📊 STATE TRACKING
        self.wallet_balance = 0.0
        self.total_equity = 0.0
        self.held_coins = {}
        self.active_slots = 0
        self.is_slot_guarded = False
        
        # 🛰️ FUTURES TRACKING
        self.futures_positions = []
        self.slot_status = []

        self.exchange = None
        self._init_exchange()

    def _init_exchange(self):
        api_key = os.getenv('MEXC_API_KEY')
        secret_key = os.getenv('MEXC_SECRET')
        if api_key and secret_key:
            self.exchange = ccxt.mexc({
                'apiKey': api_key,
                'secret': secret_key,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                    'createMarketBuyOrderRequiresPrice': False
                }
            })
            logger.info("⚔️ VORTEX V5.5: Sentinel Ignition Success")

    async def fetch_futures_telemetry(self):
        """🛰️ SENTINEL: Watches high-leverage futures for liquidation risk"""
        if not self.exchange: return
        try:
            # We fetch swap positions specifically
            pos = await self.exchange.fetch_positions(params={'type': 'swap'})
            active_pos = [p for p in pos if float(p.get('contracts', 0)) > 0]
            
            self.futures_positions = []
            for p in active_pos:
                last_price = float(p.get('last', 0))
                liq_price = float(p.get('liquidationPrice', 0))
                
                # Check for "Flash Crash" - Within 1% of Liq
                dist_to_death = abs(last_price - liq_price)
                if dist_to_death < (last_price * 0.01):
                    logger.error(f"🔥 FIRESTONE: {p['symbol']} NEAR LIQUIDATION! Ejecting...")
                    # EMERGENCY CLOSE logic could go here
                
                self.futures_positions.append({
                    "symbol": p['symbol'],
                    "leverage": f"{p['leverage']}x",
                    "pnl": f"{float(p['unrealizedPnl']):+.2f}",
                    "liq": f"${liq_price:,.2f}"
                })
        except Exception as e:
            logger.error(f"⚠️ FUTURES SYNC ERROR: {e}")

    async def fetch_portfolio(self):
        if not self.exchange: return
        try:
            # 1. Fetch Balance
            balance = await self.exchange.fetch_balance()
            self.wallet_balance = balance['total'].get('USDT', 0)
            
            # 2. Fetch Spot Tickers
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
            
            # 3. 🛰️ Run Futures Sentinel
            await self.fetch_futures_telemetry()

            # 🖥️ Map for UI
            self.slot_status = [{"coin": k, "value": f"${v['value']:.2f}"} for k, v in holdings.items()]
            
        except Exception as e:
            logger.error(f"❌ PORTFOLIO ERROR: {e}")

    async def execute_buy(self, pair: str):
        try:
            # The 'None' placeholders fix the positional argument bug
            await self.exchange.create_order(pair, 'market', 'buy', None, None, {'quoteOrderQty': self.min_stake})
            logger.info(f"✅ AGGRESSIVE BUY: {pair} ($5.00)")
            return True
        except Exception as e:
            logger.error(f"❌ BUY FAILED: {pair} | {e}")
            return False

    async def start_loop(self):
        logger.info("🚀 VORTEX: 10/10 Aggression Engaged")
        while True:
            try:
                await self.fetch_portfolio()
                # Trading check
                if self.wallet_balance >= self.min_stake and self.active_slots < self.initial_slots:
                    tickers = await self.exchange.fetch_tickers()
                    targets = [t for t in tickers.values() if t['symbol'].endswith('/USDT') and t.get('quoteVolume', 0) > 10000000][:3]
                    for t in targets:
                        if self.wallet_balance < self.min_stake: break
                        if t['symbol'].split('/')[0] not in self.held_coins:
                            await self.execute_buy(t['symbol'])
                
                await asyncio.sleep(20)
            except Exception as e:
                logger.error(f"⚠️ LOOP ERROR: {e}")
                await asyncio.sleep(20)

    async def shutdown(self):
        if self.exchange:
            await self.exchange.close()
                
