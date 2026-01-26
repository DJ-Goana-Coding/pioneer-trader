# ================================================================
# 💪 VORTEX ENGINE V4.7 - SOVEREIGN EDITION (FIXED)
# ================================================================
import os
import asyncio
import ccxt.async_support as ccxt
import pandas as pd
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
        self.trail_drop = 0.005 
        self.initial_slots = 15
        
        # 📊 STATE TRACKING
        self.wallet_balance = 0.0
        self.total_equity = 0.0
        self.total_profit = 0.0
        self.held_coins = {}
        self.peak_prices = {}
        self.active_slots = 0
        self.is_slot_guarded = False
        
        # 🔴 REDIS: Restore state
        self._restore_state_from_redis()
        
        # 🔌 MEXC HANDSHAKE
        api_key = os.getenv('MEXC_API_KEY')
        secret_key = os.getenv('MEXC_SECRET')
        
        if not api_key or not secret_key:
            logger.warning("⚠️ VORTEX: MEXC keys not found, running in BLIND MODE")
            self.exchange = None
        else:
            self.exchange = ccxt.mexc({
                'apiKey': api_key,
                'secret': secret_key,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                    'createMarketBuyOrderRequiresPrice': False
                }
            })
            logger.info("⚔️ VORTEX V4.7: SOVEREIGN Ignition Success")

    def _restore_state_from_redis(self):
        state = redis_cache.get_portfolio_state()
        if state:
            self.peak_prices = redis_cache.get_all_peaks()
            logger.info(f"🔴 REDIS: Restored {len(self.peak_prices)} peak prices")

    def _persist_state_to_redis(self):
        redis_cache.save_portfolio_state({
            'wallet_balance': self.wallet_balance,
            'total_equity': self.total_equity,
            'total_profit': self.total_profit,
            'active_slots': self.active_slots,
            'held_coins': self.held_coins
        })

    def check_slot_guard(self) -> bool:
        if self.wallet_balance < self.min_stake:
            if not self.is_slot_guarded:
                logger.warning(f"🛡️ SLOT GUARD: Balance ${self.wallet_balance:.2f} too low")
                self.is_slot_guarded = True
            return True
        self.is_slot_guarded = False
        return False

    async def fetch_portfolio(self):
        if not self.exchange: return
        try:
            balance = await self.exchange.fetch_balance()
            self.wallet_balance = balance['total'].get('USDT', 0)
            
            # 🏎️ RATE-LIMIT SHIELD: Fetch all prices in one call
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
                            
                            current_peak = redis_cache.get_peak_price(coin) or 0
                            if price > current_peak:
                                redis_cache.set_peak_price(coin, price)
            
            self.held_coins = holdings
            self.active_slots = len(holdings)
            self.total_equity = self.wallet_balance + total_holdings_value
            self.total_profit = self.total_equity - self.starting_capital
            self._persist_state_to_redis()
            
        except Exception as e:
            logger.error(f"❌ PORTFOLIO FETCH ERROR: {e}")

    async def execute_buy(self, pair: str) -> bool:
        """Sovereign execution: Spend exactly min_stake in USDT"""
        if not self.exchange: return False
        try:
            # FIX: amount=None + quoteOrderQty ensures we spend the dollar amount, not coin qty
            order = await self.exchange.create_order(
                symbol=pair,
                type='market',
                side='buy',
                amount=None, 
                params={'quoteOrderQty': self.min_stake}
            )
            logger.info(f"✅ BUY SUCCESS: {pair} | Order ID: {order.get('id', 'N/A')}")
            
            redis_cache.log_trade({
                'action': 'BUY', 'pair': pair, 'amount_usdt': self.min_stake, 'order_id': order.get('id')
            })
            return True
        except Exception as e:
            logger.error(f"❌ BUY FAILED: {pair} | REASON: {e}")
            return False

    async def start_loop(self):
        logger.info("🔍 VORTEX V4.7: SOVEREIGN MISSION ACTIVE")
        while True:
            try:
                await self.fetch_portfolio()
                now = datetime.now().strftime('%H:%M:%S')
                
                print(f"\n--- [VORTEX {now}] ---")
                print(f"💰 WALLET: ${self.wallet_balance:.2f} | 📈 EQUITY: ${self.total_equity:.2f}")
                print(f"📦 HOLDINGS: {list(self.held_coins.keys())} | 💵 P/L: ${self.total_profit:+.2f}")

                if self.check_slot_guard():
                    await asyncio.sleep(20); continue

                # 🔌 SCALPEL SCAN: Only buy if we have room and money
                tickers = await self.exchange.fetch_tickers()
                targets = [
                    t for t in tickers.values() 
                    if t['symbol'].endswith('/USDT') 
                    and t.get('quoteVolume', 0) > 5000000
                    and t['symbol'].split('/')[0] not in self.held_coins
                    and t['symbol'].split('/')[0] not in self.EXCLUDED_COINS
                ][:5] # Limited scan for safety

                for t in targets:
                    if self.wallet_balance < self.min_stake: break
                    pair = t['symbol']
                    logger.info(f"🎯 TRIGGER: {pair} detected. Engaging...")
                    await self.execute_buy(pair) # FIXED: Using the corrected method
                
                await asyncio.sleep(20)
                
            except Exception as e:
                logger.error(f"⚠️ MAIN ERROR: {e}")
                await asyncio.sleep(20)

    async def shutdown(self):
        if self.exchange:
            await self.exchange.close()
            logger.info("🔌 VORTEX: Connection closed")

        self.next_slot_price = self.min_stake
        self.slot_status = []
        self.is_slot_guarded = False
        
        # 🔴 REDIS: Restore state if available
        self._restore_state_from_redis()
        
        # 🔌 MEXC UNIVERSAL HANDSHAKE
        api_key = os.getenv('MEXC_API_KEY')
        secret_key = os.getenv('MEXC_SECRET')
        
        if not api_key or not secret_key:
            print("⚠️ VORTEX: MEXC keys not found, running in BLIND MODE")
            self.exchange = None
        else:
            self.exchange = ccxt.mexc({
                'apiKey': api_key,
                'secret': secret_key,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                    'createMarketBuyOrderRequiresPrice': False
                }
            })
            print("⚔️ VORTEX V4.6: MEXC Engine Initialized")
            print(f"🔴 REDIS: {'Connected' if redis_cache.is_connected() else 'Disabled/Unavailable'}")

    def _restore_state_from_redis(self):
        """Restore previous state from Redis on startup"""
        state = redis_cache.get_portfolio_state()
        if state:
            self.peak_prices = redis_cache.get_all_peaks()
            print(f"🔴 REDIS: Restored {len(self.peak_prices)} peak prices from cache")

    def _persist_state_to_redis(self):
        """Save current state to Redis"""
        redis_cache.save_portfolio_state({
            'wallet_balance': self.wallet_balance,
            'total_equity': self.total_equity,
            'total_profit': self.total_profit,
            'active_slots': self.active_slots,
            'held_coins': self.held_coins
        })

    def check_slot_guard(self) -> bool:
        """Returns True if trading should be HALTED"""
        if self.wallet_balance < self.min_stake:
            if not self.is_slot_guarded:
                print(f"🛡️ SLOT GUARD ACTIVATED: Balance ${self.wallet_balance:.2f} < Min ${self.min_stake}")
                self.is_slot_guarded = True
            return True
        
        if self.is_slot_guarded and self.wallet_balance >= self.min_stake:
            print(f"🛡️ SLOT GUARD RELEASED: Balance ${self.wallet_balance:.2f} >= Min ${self.min_stake}")
            self.is_slot_guarded = False
        return False

    async def fetch_portfolio(self):
        """Fetch wallet balance and holdings from MEXC"""
        if not self.exchange:
            return
            
        try:
            balance = await self.exchange.fetch_balance()
            self.wallet_balance = balance['total'].get('USDT', 0)
            
            holdings = {}
            total_holdings_value = 0.0
            
            for coin, amount in balance['total'].items():
                if amount > 0 and coin not in self.EXCLUDED_COINS:
                    try:
                        ticker = await self.exchange.fetch_ticker(f"{coin}/USDT")
                        val = amount * ticker['last']
                        if val > 1.0:
                            holdings[coin] = {
                                'amount': round(amount, 6),
                                'value': round(val, 2),
                                'price': ticker['last']
                            }
                            total_holdings_value += val
                            
                            # 🔴 REDIS: Update peak price tracking
                            current_peak = redis_cache.get_peak_price(coin) or 0
                            if ticker['last'] > current_peak:
                                redis_cache.set_peak_price(coin, ticker['last'])
                    except Exception:
                        continue
                        
            self.held_coins = holdings
            self.active_slots = len(holdings)
            self.total_equity = self.wallet_balance + total_holdings_value
            self.total_profit = self.total_equity - self.starting_capital
            
            self.slot_status = [
                {"coin": k, "value": f"${v['value']:.2f}"} 
                for k, v in holdings.items()
            ]
            
            # 🔴 REDIS: Persist state
            self._persist_state_to_redis()
            
        except Exception as e:
            logger.error(f"❌ PORTFOLIO FETCH ERROR: {e}")

    async def execute_buy(self, pair: str) -> bool:
        """Execute a market buy order with MEXC-compatible params"""
        if not self.exchange:
            return False
            
        try:
            order = await self.exchange.create_order(
                symbol=pair,
                type='market',
                side='buy',
                amount=None,
                params={'quoteOrderQty': self.min_stake}
            )
            print(f"✅ BUY SUCCESS: {pair} | Order ID: {order.get('id', 'N/A')}")
            
            # 🔴 REDIS: Log trade
            redis_cache.log_trade({
                'action': 'BUY',
                'pair': pair,
                'amount_usdt': self.min_stake,
                'order_id': order.get('id')
            })
            
            return True
            
        except Exception as e:
            print(f"❌ BUY FAILED: {pair} | REASON: {e}")
            return False

    async def start_loop(self):
        logger.info("🔍 VORTEX v4.5.2: DIAGNOSTIC MODE ACTIVE")
        """Main trading loop - runs every 20 seconds"""
        print("🔍 VORTEX V4.6: MEXC + REDIS DIAGNOSTIC MODE ACTIVE")
        
        while True:
            try:
                await self.fetch_portfolio()
                
                now = datetime.now().strftime('%H:%M:%S')
                logger.info(f"--- [DIAGNOSTIC {now}] ---")
                logger.info(f"💰 WALLET: ${self.wallet_balance:.2f} | 📦 HOLDING: {list(self.held_coins.keys())}")
                
                # Fetch only top USDT markets
                tickers = await self.exchange.fetch_tickers()
                targets = [t for t in tickers.values() if t['symbol'].endswith('/USDT') and t['quoteVolume'] > 10000000][:10]

                for t in targets:
                    pair = t['symbol']
                    if pair.split('/')[0] not in self.held_coins and self.wallet_balance > 11:
                        logger.info(f"🚀 ATTEMPTING BUY: {pair}")
                        try:
                            # ATTEMPT MARKET BUY
                            order = await self.exchange.create_order(pair, 'market', 'buy', params={'quoteOrderQty': self.min_stake})
                            logger.info(f"✅ BUY SUCCESS: {pair}")
                        except Exception as e:
                            logger.error(f"❌ BUY FAILED: {pair} | REASON: {e}")
                            await asyncio.sleep(1)
                print(f"\n--- [VORTEX {now}] ---")
                print(f"💰 WALLET: ${self.wallet_balance:.2f} | 📦 HOLDINGS: {list(self.held_coins.keys())}")
                print(f"📈 EQUITY: ${self.total_equity:.2f} | 💵 P/L: ${self.total_profit:+.2f}")
                
                if self.check_slot_guard():
                    print("⏸️ TRADING PAUSED: Insufficient balance for new slots")
                    await asyncio.sleep(20)
                    continue
                
                if self.wallet_balance < self.min_stake:
                    print(f"⏳ WAITING: Need ${self.min_stake:.2f}, have ${self.wallet_balance:.2f}")
                    await asyncio.sleep(20)
                    continue
                
                if self.exchange:
                    tickers = await self.exchange.fetch_tickers()
                    
                    targets = [
                        t for t in tickers.values() 
                        if t['symbol'].endswith('/USDT') 
                        and t.get('quoteVolume', 0) > 5000000
                        and t['symbol'].split('/')[0] not in self.EXCLUDED_COINS
                    ][:10]
                    
                    for t in targets:
                        pair = t['symbol']
                        coin = pair.split('/')[0]
                        
                        if coin in self.held_coins:
                            continue
                            
                        if self.wallet_balance < self.min_stake:
                            break
                            
                        print(f"🎯 SCANNING: {pair} | Vol: ${t.get('quoteVolume', 0):,.0f}")
                        
                await asyncio.sleep(20)
                
            except Exception as e:
                logger.error(f"⚠️ MAIN ERROR: {e}")
                await asyncio.sleep(20)
                print(f"⚠️ VORTEX ERROR: {e}")
                await asyncio.sleep(20)

    async def shutdown(self):
        """Clean shutdown of exchange connection"""
        if self.exchange:
            await self.exchange.close()
            print("🔌 VORTEX: Exchange connection closed")
