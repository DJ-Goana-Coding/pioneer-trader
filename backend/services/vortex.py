"""
🌊 VORTEX BERSERKER V3 - Sovereign Cloud Node
Fleet Configuration: 10-SLOT ARK FLEET with Bear, Crab, and Banker strategies
Enhanced with FastAPI Liveness Anchor for Hugging Face deployment
"""

import asyncio
import time
import os
import json
import base64
import threading
from typing import Dict, Optional, Tuple, List
import ccxt.async_support as ccxt
from fastapi import FastAPI
import uvicorn

from backend.core.config import settings
from backend.core.logging_config import setup_logging

logger = setup_logging("vortex")

# ================================================================
# LIVENESS ANCHOR - FastAPI Health Server (Port 7860)
# ================================================================
liveness_app = FastAPI()

@liveness_app.get("/")
async def liveness():
    """Hugging Face liveness endpoint"""
    return {
        "status": "ACTIVE",
        "commander": "Darrell",
        "fleet": "10-SLOT-VORTEX",
        "version": "V3-Enhanced"
    }

@liveness_app.get("/health")
async def health_check():
    """Additional health check endpoint"""
    return {"status": "ok", "fleet": "10-SLOT-ARK"}

def start_liveness():
    """Start liveness server in background thread"""
    uvicorn.run(liveness_app, host="0.0.0.0", port=7860, log_level="warning")

# Start liveness server immediately
threading.Thread(target=start_liveness, daemon=True).start()
logger.info("[T.I.A.] 🛡️ Liveness Anchor deployed on port 7860")


class VortexBerserker:
    """
    Sovereign Cloud Node V3 - 10-SLOT ARK FLEET
    Fleet: 2 Piranhas (scalps) + 3 Harvesters (trailing) + 2 Bears (short) + 2 Crabs (range) + 1 Banker (conservative)
    """
    
    # FLEET CONFIGURATION (10-SLOT ARK)
    PIRANHA_SLOTS = [1, 2]        # Aggressive scalps (0.4% TP)
    HARVESTER_SLOTS = [3, 4, 5]   # Trailing profit (0.5% start)
    BEAR_SLOTS = [6, 7]           # Short positions (profit on drops)
    CRAB_SLOTS = [8, 9]           # Range trading (buy low, sell high)
    BANKER_SLOT = 10              # Conservative long-term holds
    
    # CORE CONSTANTS
    PIRANHA_PROFIT_TARGET = 0.004  # 0.4%
    HARVESTER_TRAIL_START = 0.005  # 0.5%
    HARVESTER_PULLBACK_EXIT = 0.015  # 1.5%
    BEAR_PROFIT_TARGET = 0.008     # 0.8% (profit from drops)
    CRAB_RANGE_PCT = 0.006         # 0.6% range
    BANKER_PROFIT_TARGET = 0.020   # 2.0% conservative
    STOP_LOSS_PCT = 0.015  # 1.5%
    SNIPER_TP_PCT = 0.015  # 1.5%
    SNIPER_SL_PCT = 0.015  # 1.5%
    POST_BUY_COOLDOWN = 5.0  # 5 seconds
    BASE_SCAN_INTERVAL = 2.0  # 2 seconds
    
    # SCAN CONFIGURATION
    MAX_SCAN_CANDIDATES = 10
    CANDLE_TIMEFRAME = '5m'
    CANDLE_LIMIT = 50
    
    # RATE LIMITING
    RATE_LIMIT_SCAN_INTERVAL = 4.0  # 4 seconds
    RATE_LIMIT_TIMEOUT = 60  # 60 seconds
    
    # BLACKLIST (Pre-configured problematic symbols)
    INITIAL_BLACKLIST = {'PENGUIN/USDT'}
    
    def __init__(self):
        """Initialize VortexBerserker with Credential Guard"""
        self._log("🌊 10-SLOT ARK FLEET SYNCHRONIZED: 2 PIRANHAS // 3 HARVESTERS // 2 BEARS // 2 CRABS // 1 BANKER")
        
        # Credential Guard: Auto-generate credentials.json from env var
        self._setup_google_credentials()
        
        # Exchange (will be initialized in start())
        self.exchange = None
        
        # Tracking
        self.active_slots: Dict[str, dict] = {}
        self.slot_status: Dict[int, str] = {}
        self.blacklisted_symbols: set = set(self.INITIAL_BLACKLIST)
        
        # Wallet tracking
        self.wallet_balance = 0.0
        self.total_equity = 0.0
        self.total_profit = 0.0
        
        # Scan interval (adaptive)
        self.scan_interval = self.BASE_SCAN_INTERVAL
        self.rate_limit_time = 0
        
        # HuggingFace integration
        self.hf_token = os.getenv("HF_TOKEN", "")
        
        self._log(f"✅ Fleet Config: {len(self.PIRANHA_SLOTS)} Piranhas, {len(self.HARVESTER_SLOTS)} Harvesters, {len(self.BEAR_SLOTS)} Bears, {len(self.CRAB_SLOTS)} Crabs, 1 Banker")
        self._log(f"✅ Pre-blacklisted: {self.blacklisted_symbols}")
    
    def _setup_google_credentials(self):
        """
        Credential Guard: Detect GOOGLE_CREDENTIALS_B64 and auto-generate credentials.json
        """
        try:
            credentials_b64 = os.getenv("GOOGLE_CREDENTIALS_B64", "")
            if credentials_b64:
                # Decode base64 to JSON
                credentials_json = base64.b64decode(credentials_b64).decode('utf-8')
                
                # Write to credentials.json in current directory with secure permissions
                credentials_path = "credentials.json"
                with open(credentials_path, 'w') as f:
                    f.write(credentials_json)
                
                # Set secure file permissions (read/write for owner only)
                os.chmod(credentials_path, 0o600)
                
                self._log(f"🔐 Credential Guard: credentials.json generated from GOOGLE_CREDENTIALS_B64")
                
                # Set environment variable for Google libraries
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            else:
                self._log("⚠️ Credential Guard: GOOGLE_CREDENTIALS_B64 not found, skipping credential generation")
        except Exception as e:
            self._log(f"⚠️ Credential Guard error: {e}")
    
    def _log(self, msg: str):
        """Log with [T.I.A.] prefix"""
        logger.info(f"[T.I.A.] {msg}")
    
    async def start(self):
        """Main loop"""
        self._log("🚀 Starting VortexBerserker main loop...")
        
        # Initialize exchange
        if not self.exchange:
            self.exchange = ccxt.mexc({
                'apiKey': settings.MEXC_API_KEY,
                'secret': settings.MEXC_SECRET,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            await self.exchange.load_markets()
            self._log("✅ Exchange initialized")
        
        while True:
            try:
                # Adaptive rate limiting
                if time.time() < self.rate_limit_time:
                    await asyncio.sleep(1.0)
                    continue
                
                # Monitor active positions
                await self.pulse_monitor()
                
                # Scan for new opportunities
                market_data = await self.fetch_global_market()
                
                for ticker in market_data[:self.MAX_SCAN_CANDIDATES]:
                    wing, slot = self.get_available_slot_type()
                    if wing is None:
                        break
                    
                    symbol = ticker['symbol']
                    price = ticker['price']
                    
                    # Get candle data
                    candles = await self.get_candle_data(symbol)
                    if candles is None:
                        continue
                    
                    # Execute order
                    await self.execute_order(symbol, price, wing, slot)
                
                await asyncio.sleep(self.scan_interval)
                
            except Exception as e:
                self._log(f"⚠️ Main loop error: {e}")
                await asyncio.sleep(self.scan_interval)
    
    async def fetch_global_market(self) -> List[dict]:
        """
        Fetch global market tickers, filter blacklist, sort by volume/gainers
        """
        try:
            tickers = await self.exchange.fetch_tickers()
            
            # Filter and transform
            candidates = []
            for symbol, ticker in tickers.items():
                # Filter blacklist
                if symbol in self.blacklisted_symbols:
                    continue
                
                # Filter USDT pairs
                if not symbol.endswith('/USDT'):
                    continue
                
                # Extract data
                price = ticker.get('last', 0)
                volume = ticker.get('quoteVolume', 0)
                change_pct = ticker.get('percentage', 0)
                
                if price and volume:
                    candidates.append({
                        'symbol': symbol,
                        'price': price,
                        'volume': volume,
                        'change_pct': change_pct
                    })
            
            # Sort by volume (descending)
            candidates.sort(key=lambda x: x['volume'], reverse=True)
            
            return candidates
            
        except ccxt.RateLimitExceeded:
            self._log(f"⚠️ Rate limit hit - increasing scan interval to {self.RATE_LIMIT_SCAN_INTERVAL}s")
            self.scan_interval = self.RATE_LIMIT_SCAN_INTERVAL
            self.rate_limit_time = time.time() + self.RATE_LIMIT_TIMEOUT
            return []
        except Exception as e:
            self._log(f"⚠️ fetch_global_market error: {e}")
            return []
    
    def get_available_slot_type(self) -> Tuple[Optional[str], Optional[int]]:
        """
        Return next available slot
        Priority: piranha → harvester → bear → crab → banker
        Returns: (wing_type, slot_num) or (None, None) if full
        """
        # Get occupied slots
        occupied = set(data['slot'] for data in self.active_slots.values())
        
        # Check Piranha slots
        for slot in self.PIRANHA_SLOTS:
            if slot not in occupied:
                return ('piranha', slot)
        
        # Check Harvester slots
        for slot in self.HARVESTER_SLOTS:
            if slot not in occupied:
                return ('harvester', slot)
        
        # Check Bear slots
        for slot in self.BEAR_SLOTS:
            if slot not in occupied:
                return ('bear', slot)
        
        # Check Crab slots
        for slot in self.CRAB_SLOTS:
            if slot not in occupied:
                return ('crab', slot)
        
        # Check Banker slot
        if self.BANKER_SLOT not in occupied:
            return ('banker', self.BANKER_SLOT)
        
        # All slots full
        return (None, None)
    
    async def get_candle_data(self, symbol: str) -> Optional[list]:
        """
        Fetch OHLCV candle data
        Handle error 10007 blacklist
        """
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, self.CANDLE_TIMEFRAME, limit=self.CANDLE_LIMIT)
            return ohlcv
            
        except Exception as e:
            error_msg = str(e)
            # Check for error 10007 (Invalid Symbol)
            if '10007' in error_msg:
                self._log(f"🚫 Error 10007 - Blacklisting {symbol}")
                self.blacklisted_symbols.add(symbol)
            return None
    
    async def execute_order(self, symbol: str, price: float, wing: str, slot: int):
        """
        Execute buy order
        Handle error 10007 blacklist
        """
        try:
            # Calculate quantity
            stake = settings.VORTEX_STAKE_USDT
            qty = stake / price
            
            # Execute buy (always call exchange method for error handling/mocking)
            order = await self.exchange.create_market_buy_order(symbol, qty)
            
            if settings.EXECUTION_MODE != "PAPER":
                self._log(f"✅ BUY {symbol} | Wing: {wing} | Slot: {slot} | Qty: {qty:.6f}")
            else:
                self._log(f"📝 PAPER BUY {symbol} | Wing: {wing} | Slot: {slot}")
            
            # Track position
            self.active_slots[symbol] = {
                'entry': price,
                'qty': qty,
                'time': time.time(),
                'wing': wing,
                'slot': slot,
                'peak_profit': 0.0
            }
            
            # Update slot status
            self.slot_status[slot] = symbol
            
            # Push to data uplinks
            trade_data = {
                'action': 'BUY',
                'symbol': symbol,
                'price': price,
                'qty': qty,
                'wing': wing,
                'slot': slot,
                'timestamp': time.time()
            }
            self._push_to_archive(trade_data)
            if self.hf_token:
                self._push_to_hf(trade_data)
            
        except Exception as e:
            error_msg = str(e)
            # Check for error 10007 (Invalid Symbol)
            if '10007' in error_msg:
                self._log(f"🚫 Error 10007 in execute_order - Blacklisting {symbol}")
                self.blacklisted_symbols.add(symbol)
    
    async def execute_exit(self, symbol: str, qty: float, reason: str):
        """
        Execute sell order
        Handle error 30005 sync-guard
        """
        try:
            # Execute sell (always call exchange method for mocking)
            order = await self.exchange.create_market_sell_order(symbol, qty)
            
            if settings.EXECUTION_MODE != "PAPER":
                self._log(f"✅ SELL {symbol} | Reason: {reason} | Qty: {qty:.6f}")
            else:
                self._log(f"📝 PAPER SELL {symbol} | Reason: {reason}")
            
            # Clear slot
            if symbol in self.active_slots:
                slot = self.active_slots[symbol]['slot']
                del self.active_slots[symbol]
                if slot in self.slot_status:
                    del self.slot_status[slot]
            
        except ccxt.ExchangeError as e:
            error_msg = str(e)
            
            # Check for error 30005 (Oversold)
            if '30005' in error_msg:
                self._log(f"⚠️ Error 30005 (Oversold) - Sync-guard activated for {symbol}")
                
                # Check balance
                try:
                    base_currency = symbol.split('/')[0]
                    balance = await self.exchange.fetch_balance()
                    
                    actual_qty = balance.get(base_currency, {}).get('total', 0)
                    if actual_qty > 0:
                        # Balance exists - force exit
                        self._log(f"🔄 Balance detected ({actual_qty}), calling force_exit")
                        await self.force_exit(symbol, actual_qty)
                    else:
                        # No balance - just clear slot
                        self._log(f"✅ No balance detected, clearing slot")
                    
                    # Clear slot
                    if symbol in self.active_slots:
                        slot = self.active_slots[symbol]['slot']
                        del self.active_slots[symbol]
                        if slot in self.slot_status:
                            del self.slot_status[slot]
                            
                except Exception as balance_err:
                    self._log(f"⚠️ Balance check error: {balance_err}")
                    # Still clear slot
                    if symbol in self.active_slots:
                        slot = self.active_slots[symbol]['slot']
                        del self.active_slots[symbol]
                        if slot in self.slot_status:
                            del self.slot_status[slot]
        
        except Exception as e:
            self._log(f"⚠️ execute_exit error: {e}")
            # Clear slot anyway
            if symbol in self.active_slots:
                slot = self.active_slots[symbol]['slot']
                del self.active_slots[symbol]
                if slot in self.slot_status:
                    del self.slot_status[slot]
    
    async def force_exit(self, symbol: str, qty: float):
        """
        Force sell without error handling (used by sync-guard)
        """
        try:
            # Always call exchange method for mocking
            order = await self.exchange.create_market_sell_order(symbol, qty)
            
            if settings.EXECUTION_MODE != "PAPER":
                self._log(f"🔨 FORCE EXIT {symbol} | Qty: {qty:.6f}")
            else:
                self._log(f"📝 PAPER FORCE EXIT {symbol}")
        except Exception as e:
            self._log(f"⚠️ force_exit error: {e}")
    
    async def pulse_monitor(self):
        """
        Monitor all active slots
        Apply wing-specific exit logic with POST_BUY_COOLDOWN
        """
        if not self.active_slots:
            return
        
        try:
            # Fetch current prices
            tickers = await self.exchange.fetch_tickers()
            
            for symbol, position in list(self.active_slots.items()):
                # Check cooldown
                time_held = time.time() - position['time']
                if time_held < self.POST_BUY_COOLDOWN:
                    continue
                
                # Get current price
                if symbol not in tickers:
                    continue
                
                current_price = tickers[symbol].get('last')
                if not current_price:
                    continue
                entry_price = position['entry']
                profit_pct = (current_price - entry_price) / entry_price
                
                wing = position['wing']
                qty = position['qty']
                
                # Wing-specific exit logic
                if wing == 'piranha':
                    # Piranha: 0.4% profit target or -1.5% stop loss
                    if profit_pct >= self.PIRANHA_PROFIT_TARGET:
                        await self.execute_exit(symbol, qty, f"Piranha TP ({profit_pct*100:.2f}%)")
                    elif profit_pct <= -self.STOP_LOSS_PCT:
                        await self.execute_exit(symbol, qty, f"Stop Loss ({profit_pct*100:.2f}%)")
                
                elif wing == 'harvester':
                    # Harvester: Trailing with pullback exit
                    peak_profit = position['peak_profit']
                    
                    # Update peak
                    if profit_pct > peak_profit:
                        position['peak_profit'] = profit_pct
                        peak_profit = profit_pct
                    
                    # Exit conditions
                    if peak_profit >= self.HARVESTER_TRAIL_START:
                        # In profit zone - check pullback
                        pullback = peak_profit - profit_pct
                        if pullback >= self.HARVESTER_PULLBACK_EXIT:
                            await self.execute_exit(symbol, qty, f"Harvester Pullback ({profit_pct*100:.2f}%)")
                    elif profit_pct <= -self.STOP_LOSS_PCT:
                        await self.execute_exit(symbol, qty, f"Stop Loss ({profit_pct*100:.2f}%)")
                
                elif wing == 'bear':
                    # Bear: Short strategy placeholder
                    # NOTE: Currently using standard long logic with custom profit target
                    # TODO: Implement actual inverse logic for short positions in future
                    if profit_pct >= self.BEAR_PROFIT_TARGET:
                        await self.execute_exit(symbol, qty, f"Bear TP ({profit_pct*100:.2f}%)")
                    elif profit_pct <= -self.STOP_LOSS_PCT:
                        await self.execute_exit(symbol, qty, f"Bear SL ({profit_pct*100:.2f}%)")
                
                elif wing == 'crab':
                    # Crab: Range trading - exit on positive range achievement
                    # Only check positive side for exits, let stop loss handle downside
                    if profit_pct >= self.CRAB_RANGE_PCT:
                        await self.execute_exit(symbol, qty, f"Crab Range TP ({profit_pct*100:.2f}%)")
                    elif profit_pct <= -self.STOP_LOSS_PCT:
                        await self.execute_exit(symbol, qty, f"Crab SL ({profit_pct*100:.2f}%)")
                
                elif wing == 'banker':
                    # Banker: Conservative long-term - higher profit target, tight stop
                    if profit_pct >= self.BANKER_PROFIT_TARGET:
                        await self.execute_exit(symbol, qty, f"Banker TP ({profit_pct*100:.2f}%)")
                    elif profit_pct <= -self.STOP_LOSS_PCT:
                        await self.execute_exit(symbol, qty, f"Banker SL ({profit_pct*100:.2f}%)")
                
                elif wing == 'sniper':
                    # Sniper: Fixed 1.5% TP/SL (legacy support)
                    if profit_pct >= self.SNIPER_TP_PCT:
                        await self.execute_exit(symbol, qty, f"Sniper TP ({profit_pct*100:.2f}%)")
                    elif profit_pct <= -self.STOP_LOSS_PCT:
                        await self.execute_exit(symbol, qty, f"Sniper SL ({profit_pct*100:.2f}%)")
        
        except Exception as e:
            self._log(f"⚠️ pulse_monitor error: {e}")
    
    def _push_to_hf(self, trade_data: dict):
        """
        Push trade data to HuggingFace Dataset (stub implementation)
        
        NOTE: This is currently a placeholder that only logs the action.
        Actual HuggingFace Dataset API integration is not yet implemented.
        Requires HF_TOKEN environment variable to be set.
        """
        if not self.hf_token:
            return
        
        try:
            # Placeholder for HuggingFace push logic
            # TODO: Implement HuggingFace Dataset API integration
            self._log(f"📤 HF: {trade_data['action']} {trade_data['symbol']}")
        except Exception as e:
            self._log(f"⚠️ HF push error: {e}")
    
    def _push_to_archive(self, trade_data: dict):
        """Push trade data to shadow archive"""
        try:
            archive_path = settings.SHADOW_ARCHIVE_PATH
            os.makedirs(archive_path, exist_ok=True)
            
            timestamp = int(time.time())
            filename = f"{archive_path}/trade_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(trade_data, f, indent=2)
            
        except Exception as e:
            self._log(f"⚠️ Archive push error: {e}")