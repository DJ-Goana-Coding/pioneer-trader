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
    
    # INTELLIGENT STAGNATION FILTER (V3.1.0)
    MIN_HOLD_HOURS = 4.0  # Never liquidate before 4 hours
    STAGNATION_LOSS_THRESHOLD = -0.008  # -0.8% loss threshold
    STAGNATION_BREAKEVEN_MIN = -0.003  # -0.3% for breakeven range
    STAGNATION_BREAKEVEN_MAX = 0.003  # +0.3% for breakeven range
    STAGNATION_BREAKEVEN_HOURS = 8.0  # 8 hours for breakeven stagnation
    
    # MLOFI GATEKEEPER (V3.1.0)
    HIGH_LIQUIDITY_THRESHOLD = 50_000_000  # $50M volume
    MID_LIQUIDITY_THRESHOLD = 10_000_000  # $10M volume
    MLOFI_STRICT_MIN = 0  # Strict MLOFI > 0 for high liquidity
    MLOFI_MID_MIN = -0.15  # Allow -0.15 for mid liquidity
    RSI_OVERSOLD_THRESHOLD = 25  # Extreme oversold RSI
    
    # DYNAMIC POSITION SIZING (V3.1.0)
    POSITION_SIZE_PCT = 0.04  # 4% of equity per trade
    MIN_POSITION_SIZE = 5.0  # Minimum $5 USDT
    MAX_POSITION_SIZE = 15.0  # Maximum $15 USDT
    
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
    
    # ================================================================
    # INTELLIGENT STAGNATION FILTER (V3.1.0)
    # ================================================================
    
    async def _get_price_30min_ago(self, symbol: str, current_price: float) -> Optional[float]:
        """
        Get price from 30 minutes ago for momentum analysis.
        Uses 5-minute candles, so 30 minutes ago = 6 candles back.
        
        Returns:
            Price from 30 minutes ago, or None if data unavailable
        """
        try:
            candles = await self.get_candle_data(symbol)
            if not candles or len(candles) < 7:
                # Not enough data, return None
                return None
            
            # Get the closing price from 6 candles ago (30 minutes)
            # candles[-1] is current, candles[-7] is 30 minutes ago
            price_30min_ago = candles[-7][4]  # Index 4 is the close price
            return price_30min_ago
            
        except Exception as e:
            self._log(f"⚠️ Error getting 30-min price for {symbol}: {e}")
            return None
    
    async def _showing_recovery_momentum(self, symbol: str, current_price: float, entry_price: float) -> bool:
        """
        Check if price is recovering (comparing current to 30-min-ago price).
        
        Returns:
            True if price is trending upward, False otherwise
        """
        try:
            price_30min_ago = await self._get_price_30min_ago(symbol, current_price)
            
            if price_30min_ago is None:
                # No data available - assume no recovery
                self._log(f"🔍 {symbol}: No 30-min price data, assuming no recovery")
                return False
            
            # Calculate momentum (positive = recovering)
            momentum_pct = ((current_price - price_30min_ago) / price_30min_ago) * 100
            
            # Consider recovery if momentum is positive
            is_recovering = momentum_pct > 0
            
            if is_recovering:
                self._log(f"📈 {symbol}: Recovery momentum detected (+{momentum_pct:.3f}% over 30min)")
            else:
                self._log(f"📉 {symbol}: No recovery momentum ({momentum_pct:.3f}% over 30min)")
            
            return is_recovering
            
        except Exception as e:
            self._log(f"⚠️ Error checking recovery momentum for {symbol}: {e}")
            return False
    
    async def should_liquidate_stagnant(self, symbol: str, entry_time: float, entry_price: float, 
                                       current_price: float) -> Tuple[bool, str]:
        """
        Intelligent stagnation detection - only liquidate truly dead trades.
        
        Rules:
        1. Never liquidate before 4 hours
        2. Liquidate if loss > 0.8% AND no recovery momentum (price declining over last 30 min)
        3. Extended hold for near-breakeven positions (free up capital after 8 hours if -0.3% < profit < +0.3%)
        4. NEVER force-sell positions showing recovery signs
        
        Returns:
            Tuple of (should_liquidate: bool, reason: str)
        """
        current_hours = (time.time() - entry_time) / 3600
        
        # Rule 1: Never liquidate before 4 hours
        if current_hours < self.MIN_HOLD_HOURS:
            return (False, "")
        
        loss_pct = ((current_price - entry_price) / entry_price)
        
        # Rule 2: Critical loss threshold with momentum check
        if loss_pct < self.STAGNATION_LOSS_THRESHOLD:
            # Check recovery momentum
            has_recovery = await self._showing_recovery_momentum(symbol, current_price, entry_price)
            
            if not has_recovery:
                reason = f"Stagnation: Loss {loss_pct*100:.2f}% with no recovery ({current_hours:.1f}h)"
                self._log(f"🚨 {symbol}: {reason}")
                return (True, reason)
            else:
                self._log(f"⏳ {symbol}: Loss {loss_pct*100:.2f}% but showing recovery - holding")
                return (False, "")
        
        # Rule 3: Free up capital from dead sideways trades
        if (self.STAGNATION_BREAKEVEN_MIN < loss_pct < self.STAGNATION_BREAKEVEN_MAX and 
            current_hours > self.STAGNATION_BREAKEVEN_HOURS):
            reason = f"Stagnation: Sideways {loss_pct*100:.2f}% for {current_hours:.1f}h"
            self._log(f"⏹️ {symbol}: {reason}")
            return (True, reason)
        
        return (False, "")
    
    # ================================================================
    # CONTEXT-AWARE MLOFI GATEKEEPER (V3.1.0)
    # ================================================================
    
    async def _get_price_momentum(self, symbol: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Calculate short-term price momentum (1h and 4h price change).
        
        Returns:
            Tuple of (momentum_1h_pct, momentum_4h_pct) or (None, None) if data unavailable
        """
        try:
            candles = await self.get_candle_data(symbol)
            if not candles or len(candles) < 49:
                return (None, None)
            
            current_price = candles[-1][4]  # Latest close price
            
            # 1-hour momentum (12 candles ago at 5-minute intervals)
            if len(candles) >= 13:
                price_1h_ago = candles[-13][4]
                momentum_1h = ((current_price - price_1h_ago) / price_1h_ago) * 100
            else:
                momentum_1h = None
            
            # 4-hour momentum (48 candles ago at 5-minute intervals)
            if len(candles) >= 49:
                price_4h_ago = candles[-49][4]
                momentum_4h = ((current_price - price_4h_ago) / price_4h_ago) * 100
            else:
                momentum_4h = None
            
            return (momentum_1h, momentum_4h)
            
        except Exception as e:
            self._log(f"⚠️ Error calculating price momentum for {symbol}: {e}")
            return (None, None)
    
    async def _check_price_momentum_positive(self, symbol: str) -> bool:
        """
        Check if short-term price momentum is positive.
        Returns True if both 1h and 4h momentum are positive.
        """
        try:
            momentum_1h, momentum_4h = await self._get_price_momentum(symbol)
            
            if momentum_1h is None or momentum_4h is None:
                # No data available - be conservative
                return False
            
            # Both should be positive for low-liquidity pairs
            is_positive = momentum_1h > 0 and momentum_4h > 0
            
            if is_positive:
                self._log(f"✅ {symbol}: Positive momentum (1h: +{momentum_1h:.2f}%, 4h: +{momentum_4h:.2f}%)")
            else:
                self._log(f"❌ {symbol}: Negative momentum (1h: {momentum_1h:.2f}%, 4h: {momentum_4h:.2f}%)")
            
            return is_positive
            
        except Exception as e:
            self._log(f"⚠️ Error checking price momentum for {symbol}: {e}")
            return False
    
    async def is_buy_allowed(self, symbol: str, volume_24h: float, candles: Optional[list] = None) -> Tuple[bool, str]:
        """
        Context-aware MLOFI gatekeeper - adapts to liquidity conditions.
        
        Rules:
        - High liquidity (>$50M volume): Strict MLOFI > 0 requirement (not implemented - no MLOFI data)
        - Mid liquidity ($10M-$50M): Allow if RSI < 25 (extreme oversold)
        - Low liquidity (<$10M): Use price momentum instead
        
        Note: MLOFI calculation not implemented yet, using simplified logic
        
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        try:
            # Fetch candles if not provided
            if candles is None:
                candles = await self.get_candle_data(symbol)
            
            if not candles or len(candles) < 14:
                return (False, f"Insufficient candle data")
            
            # Calculate RSI (14-period)
            closes = [candle[4] for candle in candles[-14:]]
            rsi = self._calculate_rsi(closes, period=14)
            
            # High-liquidity pairs: Would require MLOFI > 0 (not implemented)
            if volume_24h > self.HIGH_LIQUIDITY_THRESHOLD:
                # Since we don't have MLOFI, use RSI as proxy
                if rsi is not None and rsi < 30:
                    self._log(f"💎 {symbol}: High liquidity, RSI {rsi:.1f} (oversold) - ALLOWED")
                    return (True, f"High liquidity with RSI {rsi:.1f}")
                else:
                    self._log(f"⛔ {symbol}: High liquidity, RSI {rsi:.1f if rsi else 'N/A'} - BLOCKED")
                    return (False, f"High liquidity without oversold signal")
            
            # Mid-liquidity: Allow exceptions for extreme oversold
            if volume_24h > self.MID_LIQUIDITY_THRESHOLD:
                if rsi is not None and rsi < self.RSI_OVERSOLD_THRESHOLD:
                    self._log(f"💎 {symbol}: Mid liquidity, extreme oversold RSI {rsi:.1f} - ALLOWED")
                    return (True, f"Mid liquidity with extreme oversold RSI {rsi:.1f}")
                else:
                    self._log(f"⛔ {symbol}: Mid liquidity, RSI {rsi:.1f if rsi else 'N/A'} - BLOCKED")
                    return (False, f"Mid liquidity without extreme oversold")
            
            # Low-liquidity: Use price momentum instead
            momentum_positive = await self._check_price_momentum_positive(symbol)
            if momentum_positive:
                self._log(f"💎 {symbol}: Low liquidity with positive momentum - ALLOWED")
                return (True, "Low liquidity with positive momentum")
            else:
                self._log(f"⛔ {symbol}: Low liquidity without positive momentum - BLOCKED")
                return (False, "Low liquidity without positive momentum")
            
        except Exception as e:
            self._log(f"⚠️ Error in MLOFI gatekeeper for {symbol}: {e}")
            return (False, f"Error: {str(e)}")
    
    def _calculate_rsi(self, prices: list, period: int = 14) -> Optional[float]:
        """
        Calculate RSI (Relative Strength Index).
        
        Args:
            prices: List of closing prices (at least period+1 length)
            period: RSI period (default 14)
        
        Returns:
            RSI value (0-100) or None if insufficient data
        """
        try:
            if len(prices) < period + 1:
                return None
            
            # Calculate price changes
            deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
            
            # Separate gains and losses
            gains = [d if d > 0 else 0 for d in deltas]
            losses = [-d if d < 0 else 0 for d in deltas]
            
            # Calculate average gain and loss
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
            
            # Avoid division by zero
            if avg_loss == 0:
                return 100.0
            
            # Calculate RS and RSI
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            self._log(f"⚠️ Error calculating RSI: {e}")
            return None
    
    # ================================================================
    # DYNAMIC POSITION SIZING (V3.1.0)
    # ================================================================
    
    def calculate_position_size(self, total_equity: float) -> float:
        """
        Calculate safe position size based on remaining capital.
        
        Rules:
        - Max 4% of total equity per trade
        - Minimum position size: $5 USDT
        - Maximum position size: $15 USDT (even if capital grows)
        
        Args:
            total_equity: Current total equity in USDT
        
        Returns:
            Position size in USDT
        """
        max_stake = total_equity * self.POSITION_SIZE_PCT
        
        # Enforce boundaries
        stake = max(self.MIN_POSITION_SIZE, min(max_stake, self.MAX_POSITION_SIZE))
        
        self._log(f"💰 Position sizing: Equity=${total_equity:.2f} → Stake=${stake:.2f} (4% rule)")
        
        return stake
    
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
                    volume_24h = ticker['volume']
                    
                    # Get candle data
                    candles = await self.get_candle_data(symbol)
                    if candles is None:
                        continue
                    
                    # MLOFI Gatekeeper (V3.1.0): Context-aware filtering
                    buy_allowed, reason = await self.is_buy_allowed(symbol, volume_24h, candles)
                    if not buy_allowed:
                        self._log(f"🚫 {symbol}: MLOFI gatekeeper blocked - {reason}")
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
        Execute buy order with dynamic position sizing
        Handle error 10007 blacklist
        """
        try:
            # Dynamic position sizing (V3.1.0)
            # Use total_equity if available, otherwise fall back to wallet_balance or config
            equity = self.total_equity if self.total_equity > 0 else (
                self.wallet_balance if self.wallet_balance > 0 else 100.0  # Default $100 capital
            )
            stake = self.calculate_position_size(equity)
            qty = stake / price
            
            # Execute buy (always call exchange method for error handling/mocking)
            order = await self.exchange.create_market_buy_order(symbol, qty)
            
            if settings.EXECUTION_MODE != "PAPER":
                self._log(f"✅ BUY {symbol} | Wing: {wing} | Slot: {slot} | Qty: {qty:.6f} | Stake: ${stake:.2f}")
            else:
                self._log(f"📝 PAPER BUY {symbol} | Wing: {wing} | Slot: {slot} | Stake: ${stake:.2f}")
            
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
                entry_time = position['time']
                profit_pct = (current_price - entry_price) / entry_price
                
                wing = position['wing']
                qty = position['qty']
                
                # Intelligent Stagnation Filter (V3.1.0)
                # Check for stagnant positions before wing-specific logic
                should_liquidate, stagnation_reason = await self.should_liquidate_stagnant(
                    symbol, entry_time, entry_price, current_price
                )
                if should_liquidate:
                    await self.execute_exit(symbol, qty, stagnation_reason)
                    continue  # Skip wing-specific logic
                
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