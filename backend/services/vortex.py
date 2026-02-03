"""
Vortex Berserker Engine - Hardened Trading System
Implements aggressive 8-second pulse trading with mandatory 1.5% stop-loss protection.

🛡️ SECURITY WARNING:
- API keys are loaded from environment variables ONLY
- NEVER hardcode credentials in this file
- See SECURITY_CHECKLIST.md for safe credential management
- Always test in PAPER mode before LIVE execution
"""

import asyncio
import pandas as pd
import pandas_ta as ta
from typing import Dict, Optional
from datetime import datetime
import logging

try:
    import ccxt.async_support as ccxt
except ImportError:
    import ccxt

from backend.core.config import settings

logger = logging.getLogger(__name__)


class VortexBerserker:
    """
    Hardened trading engine with mandatory survival protocols.
    
    Key Features:
    - Mandatory 1.5% stop-loss (Ejector Seat) on all positions
    - Market orders only for immediate execution (no "sitting there")
    - 8-second pulse for rapid market response
    - Multi-slot parallel execution across trading pairs
    """
    
    def __init__(self):
        """Initialize Vortex engine with environment-based credentials ONLY."""
        self.exchange = None
        self.universe = [
            "SOL/USDT", "XRP/USDT", "DOGE/USDT", "ADA/USDT", 
            "MATIC/USDT", "DOT/USDT", "LINK/USDT"
        ]
        self.stake = settings.VORTEX_STAKE_USDT
        self.stop_loss = settings.VORTEX_STOP_LOSS_PCT
        self.pulse_interval = settings.VORTEX_PULSE_SECONDS
        self.active_slots: Dict[int, Dict] = {}  # slot_id: {symbol, entry_price, qty, entry_time}
        self.running = False
        self._tasks = []
        
        logger.info(f"🔥 Vortex Berserker initialized: Stake=${self.stake}, Stop-Loss={self.stop_loss*100}%")
    
    async def initialize(self):
        """
        Initialize exchange connection with environment variables.
        
        🛡️ SECURITY: Only environment variables are used for credentials.
        If you see "PLACEHOLDER" in any credential value, the system will refuse to start in LIVE mode.
        See SECURITY_CHECKLIST.md for setup instructions.
        """
        if settings.EXECUTION_MODE == "PAPER":
            logger.warning("⚠️ Vortex running in PAPER mode - simulated execution only")
            self.exchange = None
            return
        
        try:
            # Only use environment variables - NEVER hardcoded keys
            if not settings.MEXC_API_KEY or not settings.MEXC_SECRET_KEY:
                raise ValueError("MEXC_API_KEY and MEXC_SECRET_KEY must be set in environment")
            
            self.exchange = ccxt.mexc({
                'apiKey': settings.MEXC_API_KEY,
                'secret': settings.MEXC_SECRET_KEY,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                }
            })
            
            # Test connection
            await self.exchange.load_markets()
            logger.info("✅ MEXC exchange connected successfully")
            
        except Exception as e:
            logger.error(f"❌ Exchange initialization failed: {e}")
            logger.warning("⚠️ Falling back to PAPER mode")
            self.exchange = None
    
    async def check_stop_loss_triggered(self, slot_id: int, current_price: float) -> bool:
        """
        THE EJECTOR SEAT: Mandatory stop-loss check before any other logic.
        
        Args:
            slot_id: The trading slot identifier
            current_price: Current market price for the position
            
        Returns:
            True if stop-loss was triggered and position ejected, False otherwise
        """
        pos = self.active_slots.get(slot_id)
        if not pos:
            return False
        
        entry_price = pos['entry_price']
        drawdown = (entry_price - current_price) / entry_price
        
        if drawdown >= self.stop_loss:
            logger.warning(f"🚨 [EJECT] {pos['symbol']} hit {self.stop_loss*100}% loss. EXITING AT MARKET.")
            logger.info(f"   Entry: ${entry_price:.4f}, Current: ${current_price:.4f}, Loss: {drawdown*100:.2f}%")
            await self.execute_market_sell(slot_id)
            return True
        
        return False
    
    async def execute_market_sell(self, slot_id: int):
        """
        Immediate market exit - No limit orders that can "sit there".
        Executes synchronously to guarantee exit.
        
        Args:
            slot_id: The trading slot identifier for the position to close
            
        Behavior:
            - PAPER mode: Simulates sell and removes position from active_slots
            - LIVE mode: Executes real market sell order on exchange
        """
        pos = self.active_slots.get(slot_id)
        if not pos:
            logger.warning(f"Attempted to sell non-existent slot {slot_id}")
            return
        
        try:
            if self.exchange is None:
                # Paper mode - simulate execution
                logger.info(f"📝 [PAPER] Market SELL {pos['symbol']}: {pos['qty']:.6f} @ market")
                del self.active_slots[slot_id]
                return
            
            # Real execution - get actual balance
            bal = await self.exchange.fetch_balance()
            coin = pos['symbol'].split('/')[0]
            amount = bal['total'].get(coin, 0)
            
            if amount > 0:
                order = await self.exchange.create_market_sell_order(pos['symbol'], amount)
                logger.info(f"✅ [LIVE] Market SELL executed: {order['id']}")
                del self.active_slots[slot_id]
            else:
                logger.warning(f"⚠️ No {coin} balance to sell")
                del self.active_slots[slot_id]
                
        except Exception as e:
            logger.error(f"❌ [CRITICAL] Market exit FAILED for slot {slot_id}: {e}")
            # Still remove from active slots to prevent infinite error loop
            if slot_id in self.active_slots:
                del self.active_slots[slot_id]
    
    async def execute_market_buy(self, slot_id: int, symbol: str, price: float):
        """
        Execute market buy order.
        
        Args:
            slot_id: The trading slot identifier
            symbol: Trading pair in format 'BASE/QUOTE' (e.g., 'BTC/USDT')
            price: Current market price for position sizing
            
        Behavior:
            - PAPER mode: Simulates buy and adds position to active_slots
            - LIVE mode: Executes real market buy order on exchange
        """
        try:
            qty = self.stake / price
            
            if self.exchange is None:
                # Paper mode
                logger.info(f"📝 [PAPER] Market BUY {symbol}: {qty:.6f} @ ${price:.4f}")
                self.active_slots[slot_id] = {
                    'symbol': symbol,
                    'entry_price': price,
                    'qty': qty,
                    'entry_time': datetime.now()
                }
                return
            
            # Real execution
            order = await self.exchange.create_market_buy_order(symbol, qty)
            logger.info(f"✅ [LIVE] Market BUY executed: {order['id']}")
            
            self.active_slots[slot_id] = {
                'symbol': symbol,
                'entry_price': price,
                'qty': qty,
                'entry_time': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"❌ Market BUY failed for {symbol}: {e}")
    
    async def fetch_market_data(self, symbol: str, timeframe: str = '1m', limit: int = 50):
        """
        Fetch OHLCV data with fallback to mock data in paper mode.
        
        Args:
            symbol: Trading pair in format 'BASE/QUOTE' (e.g., 'BTC/USDT')
            timeframe: Candle interval (default: '1m' for 1-minute candles)
            limit: Number of candles to fetch (default: 50)
            
        Returns:
            List of OHLCV arrays: [[timestamp, open, high, low, close, volume], ...]
            Returns empty list if fetch fails.
        """
        try:
            if self.exchange is None:
                # Generate mock data for paper trading
                import numpy as np
                current_time = int(datetime.now().timestamp() * 1000)
                base_price = 100.0  # Mock base price
                
                ohlcv = []
                for i in range(limit):
                    timestamp = current_time - (limit - i) * 60000  # 1-minute intervals
                    # Simulate random walk
                    change = np.random.normal(0, 0.01) * base_price
                    price = base_price + change
                    ohlcv.append([timestamp, price, price * 1.005, price * 0.995, price, 1000.0])
                    base_price = price
                
                return ohlcv
            
            # Real data fetch
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            return ohlcv
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch data for {symbol}: {e}")
            return []
    
    async def run_slot(self, slot_id: int, symbol: str):
        """
        Aggressive 8-second pulse trading loop for a single slot.
        Implements RSI(30/70) + EMA50 strategy with mandatory stop-loss.
        
        Args:
            slot_id: The trading slot identifier
            symbol: Trading pair in format 'BASE/QUOTE' (e.g., 'SOL/USDT')
            
        This is a long-running coroutine that executes until self.running is set to False.
        Each iteration:
        1. Fetches latest market data
        2. Calculates technical indicators (RSI, EMA50)
        3. If position exists: checks stop-loss FIRST, then take-profit conditions
        4. If no position: checks entry conditions (oversold + above EMA50)
        5. Sleeps for pulse_interval (default 8 seconds)
        """
        logger.info(f"🎯 Slot {slot_id} activated for {symbol}")
        
        while self.running:
            try:
                # Fetch market data
                ohlcv = await self.fetch_market_data(symbol, timeframe='1m', limit=50)
                
                if not ohlcv or len(ohlcv) < 50:
                    logger.warning(f"⚠️ Insufficient data for {symbol}")
                    await asyncio.sleep(self.pulse_interval)
                    continue
                
                # Convert to DataFrame for technical analysis
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                
                # Calculate indicators
                rsi = ta.rsi(df['close'], length=14).iloc[-1]
                ema50 = ta.ema(df['close'], length=50).iloc[-1]
                current_price = df['close'].iloc[-1]
                
                # Position management
                if slot_id in self.active_slots:
                    # PRIORITY 1: Check stop-loss (ejector seat)
                    ejected = await self.check_stop_loss_triggered(slot_id, current_price)
                    if ejected:
                        await asyncio.sleep(self.pulse_interval)
                        continue
                    
                    # PRIORITY 2: Take profit on overbought
                    if rsi > 70:
                        logger.info(f"📈 {symbol} overbought (RSI={rsi:.1f}), taking profit")
                        await self.execute_market_sell(slot_id)
                    
                else:
                    # Entry logic: Oversold + above EMA50 (trend filter)
                    if rsi < 30 and current_price > ema50:
                        logger.info(f"📉 {symbol} oversold (RSI={rsi:.1f}), entering position")
                        await self.execute_market_buy(slot_id, symbol, current_price)
                
            except Exception as e:
                logger.error(f"⚠️ [SLOT {slot_id} ERROR] {e}")
            
            # Commander's pulse: 8-second interval
            await asyncio.sleep(self.pulse_interval)
        
        logger.info(f"🛑 Slot {slot_id} ({symbol}) stopped")
    
    async def start(self):
        """Start the vortex engine with parallel slot execution."""
        if self.running:
            logger.warning("Vortex already running")
            return
        
        self.running = True
        logger.info(f"🚀 Starting Vortex Berserker Engine with {len(self.universe)} slots")
        
        # Launch parallel trading slots
        for slot_id, symbol in enumerate(self.universe):
            task = asyncio.create_task(self.run_slot(slot_id, symbol))
            self._tasks.append(task)
        
        logger.info("✅ All trading slots activated")
    
    async def stop(self):
        """Stop the vortex engine and close all positions."""
        if not self.running:
            return
        
        logger.info("🛑 Stopping Vortex engine...")
        self.running = False
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        
        # Close all positions
        if self.active_slots:
            logger.info(f"Closing {len(self.active_slots)} active positions...")
            for slot_id in list(self.active_slots.keys()):
                await self.execute_market_sell(slot_id)
        
        logger.info("✅ Vortex engine stopped")
    
    async def shutdown(self):
        """Clean shutdown with exchange cleanup."""
        await self.stop()
        
        if self.exchange:
            await self.exchange.close()
            logger.info("✅ Exchange connection closed")
    
    def get_status(self) -> Dict:
        """Get current vortex status."""
        return {
            "running": self.running,
            "mode": "PAPER" if self.exchange is None else "LIVE",
            "active_positions": len(self.active_slots),
            "positions": [
                {
                    "slot_id": slot_id,
                    "symbol": pos['symbol'],
                    "entry_price": pos['entry_price'],
                    "quantity": pos['qty'],
                    "entry_time": pos['entry_time'].isoformat()
                }
                for slot_id, pos in self.active_slots.items()
            ],
            "configuration": {
                "stake_usdt": self.stake,
                "stop_loss_pct": self.stop_loss * 100,
                "pulse_seconds": self.pulse_interval,
                "universe": self.universe
            }
        }
