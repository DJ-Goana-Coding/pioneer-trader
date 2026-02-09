import os, asyncio, ccxt.async_support as ccxt
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import time
from backend.core.logging_config import setup_logging

logger = setup_logging("vortex")

class VortexBerserker:
    # Hybrid Swarm Slot Architecture
    PIRANHA_SLOTS = [1, 2, 3, 4]  # Wing A: Fast momentum (0.4% exits)
    HARVESTER_SLOTS = [5, 6, 7]   # Wing B: Trailing grid
    
    # Trading Parameters
    PIRANHA_PROFIT_TARGET = 0.004  # 0.4% fixed profit exit
    HARVESTER_TRAIL_START = 0.005  # 0.5% profit to start trailing
    HARVESTER_PULLBACK_EXIT = 0.015  # 1.5% pullback from peak to exit
    STOP_LOSS_PCT = 0.015  # 1.5% hard stop loss for both wings
    
    # Market Scanning Parameters
    TOP_MOVERS_LIMIT = 10  # Number of top movers to check for entry signals
    
    # Sync-Guard Parameters
    POST_BUY_COOLDOWN = 5.0  # 5-second cooldown after buy before allowing sell
    
    def __init__(self):
        self.base_stake = 8.00 
        self.max_slots = 7
        self.stop_loss_pct = self.STOP_LOSS_PCT
        self.active_slots = {}  # {symbol: {'entry': price, 'qty': amount, 'time': timestamp, 'wing': 'piranha'|'harvester', 'slot': 1-7, 'peak_profit': 0.0}}
        self.exchange = None
        self.current_pulse = 2  # Adaptive pulse: 2s default, 4s on rate limit
        self.pulse_reset_time = None  # Track when to reset pulse
        self.blacklisted_symbols = set()  # Symbols that returned error 10007
        self._init_mexc()

    def _init_mexc(self):
        """Live Connection to MEXC."""
        self.exchange = ccxt.mexc({
            'apiKey': os.getenv('MEXC_API_KEY'),
            'secret': os.getenv('MEXC_SECRET'),
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })

    async def fetch_global_market(self) -> list:
        """Global Market Scanner: Entire MEXC USDT market."""
        try:
            all_tickers = await self.exchange.fetch_tickers()
            
            # Filter to USDT pairs with sufficient volume
            filtered = []
            for symbol, ticker in all_tickers.items():
                # Skip blacklisted symbols (error 10007)
                if symbol in self.blacklisted_symbols:
                    continue
                    
                if symbol.endswith('/USDT') and ticker.get('quoteVolume', 0) > 500000:
                    # Using 24h percentage change for sorting market movers
                    # This helps identify hot symbols for both wings:
                    # - Piranha: Checks green candle on hot symbols for momentum
                    # - Harvester: Selects top movers directly
                    change_24h = ticker.get('percentage', 0)
                    filtered.append({
                        'symbol': symbol,
                        'volume_24h': ticker.get('quoteVolume', 0),
                        'change_24h': change_24h,
                        'last': ticker.get('last', 0)
                    })
            
            # Sort by 24h change (descending) - strongest movers first
            sorted_tickers = sorted(filtered, key=lambda x: x['change_24h'], reverse=True)
            return sorted_tickers
            
        except ccxt.RateLimitExceeded:
            self._log("⚠️ RATE LIMIT: Activating adaptive throttle")
            self.current_pulse = 4
            self.pulse_reset_time = time.time() + 60
            return []
        except Exception as e:
            self._log(f"⚠️ MARKET SCAN ERROR: {e}")
            return []
    
    async def get_candle_data(self, symbol: str) -> dict:
        """Fetch 1-minute candle data for momentum detection."""
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe='1m', limit=2)
            if len(ohlcv) < 2:
                return None
            df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
            return df
        except Exception as e:
            # Check for error code 10007 (invalid symbol)
            error_str = str(e)
            if '10007' in error_str:
                self.blacklisted_symbols.add(symbol)
                self._log(f"🚫 BLACKLIST: {symbol} (Error 10007 - Invalid symbol)")
            else:
                self._log(f"⚠️ CANDLE ERROR {symbol}: {e}")
            return None

    def get_available_slot_type(self):
        """Determine which wing has available slots."""
        occupied_slots = [pos.get('slot') for pos in self.active_slots.values()]
        
        # Check Piranha slots (1-4)
        for slot in self.PIRANHA_SLOTS:
            if slot not in occupied_slots:
                return ('piranha', slot)
        
        # Check Harvester slots (5-7)
        for slot in self.HARVESTER_SLOTS:
            if slot not in occupied_slots:
                return ('harvester', slot)
        
        return (None, None)
    
    async def scout_and_buy(self):
        """Hybrid Swarm Scanner: Separate logic for Piranha vs Harvester wings."""
        if len(self.active_slots) >= self.max_slots: 
            return

        wing_type, slot_num = self.get_available_slot_type()
        if wing_type is None:
            return
        
        try:
            market_data = await self.fetch_global_market()
            if not market_data:
                return
            
            if wing_type == 'piranha':
                # Piranha Wing: Green candle momentum (Close > Open)
                # Check top movers first, then validate with green candle
                for ticker in market_data[:self.TOP_MOVERS_LIMIT]:
                    symbol = ticker['symbol']
                    if symbol in self.active_slots:
                        continue
                    
                    df = await self.get_candle_data(symbol)
                    if df is None or len(df) < 2:
                        continue
                    
                    last_candle = df.iloc[-1]
                    is_green = last_candle['close'] > last_candle['open']
                    
                    if is_green:
                        self._log(f"🦈 PIRANHA SIGNAL: {symbol} (Green Candle)")
                        await self.execute_order(symbol, last_candle['close'], wing_type, slot_num)
                        return  # One entry per cycle
                        
            elif wing_type == 'harvester':
                # Harvester Wing: Top market movers by 24h % change
                # Check top movers to ensure we can find available symbols
                top_movers = [t for t in market_data[:self.TOP_MOVERS_LIMIT] if t['symbol'] not in self.active_slots]
                if top_movers:
                    ticker = top_movers[0]
                    symbol = ticker['symbol']
                    self._log(f"🌾 HARVESTER SIGNAL: {symbol} (Top Mover: {ticker['change_24h']:.2f}%)")
                    await self.execute_order(symbol, ticker['last'], wing_type, slot_num)
                    
        except ccxt.RateLimitExceeded:
            self._log("⚠️ RATE LIMIT: Activating adaptive throttle")
            self.current_pulse = 4
            self.pulse_reset_time = time.time() + 60
        except Exception as e:
            self._log(f"⚠️ SCAN ERROR: {e}")

    async def execute_order(self, symbol, price, wing_type, slot_num):
        try:
            # Calculate exact amount (Base Currency)
            amount = self.base_stake / price
            order = await self.exchange.create_market_buy_order(symbol, amount)
            self.active_slots[symbol] = {
                'entry': price, 
                'qty': amount, 
                'time': time.time(),
                'wing': wing_type,
                'slot': slot_num,
                'peak_profit': 0.0  # For trailing stop (Harvester wing)
            }
            wing_emoji = "🦈" if wing_type == 'piranha' else "🌾"
            self._log(f"🔥 FILLED: {wing_emoji} Slot {slot_num} | {symbol} @ ${price:.4f}")
        except Exception as e:
            # Check for error code 10007 (symbol not support api)
            error_str = str(e)
            if '10007' in error_str:
                self.blacklisted_symbols.add(symbol)
                self._log(f"🚫 BLACKLIST: {symbol} (Error 10007 - Symbol not supported)")
            self._log(f"❌ BUY FAILED: {e}")

    async def pulse_monitor(self):
        """Hybrid Exit Logic: Piranha (0.4% fixed) vs Harvester (trailing grid)."""
        if not self.active_slots: 
            return
        
        try:
            tickers = await self.exchange.fetch_tickers(list(self.active_slots.keys()))
            
            for sym, pos in list(self.active_slots.items()):
                # Sync-Guard: Enforce post-buy cooldown (5 seconds)
                time_held = time.time() - pos['time']
                if time_held < self.POST_BUY_COOLDOWN:
                    # Log at debug level for troubleshooting
                    logger.debug(f"⏳ Cooldown active: {sym} held for {time_held:.1f}s/{self.POST_BUY_COOLDOWN}s")
                    continue  # Skip this slot until cooldown expires
                
                curr_price = tickers[sym]['last']
                profit_pct = (curr_price - pos['entry']) / pos['entry']
                
                if pos['wing'] == 'piranha':
                    # Piranha Wing: Fixed 0.4% take-profit
                    if profit_pct >= self.PIRANHA_PROFIT_TARGET:
                        await self.execute_exit(sym, pos['qty'], f"💰 PIRANHA PROFIT (Slot {pos['slot']})")
                    # Stop loss at -1.5%
                    elif profit_pct <= -self.STOP_LOSS_PCT:
                        await self.execute_exit(sym, pos['qty'], f"🛡️ PIRANHA STOP (Slot {pos['slot']})")
                
                elif pos['wing'] == 'harvester':
                    # Harvester Wing: Trailing Grid System
                    # Update peak profit
                    if profit_pct > pos['peak_profit']:
                        old_peak = pos['peak_profit']
                        pos['peak_profit'] = profit_pct
                        # Log only significant trailing activations (every 0.5% increment)
                        if profit_pct >= self.HARVESTER_TRAIL_START and (old_peak == 0 or profit_pct - old_peak >= 0.005):
                            self._log(f"📈 HARVESTER TRAILING: {sym} Peak: {pos['peak_profit']*100:.2f}%")
                    
                    # Exit on 1.5% pullback from peak
                    pullback = pos['peak_profit'] - profit_pct
                    if pos['peak_profit'] > 0 and pullback >= self.HARVESTER_PULLBACK_EXIT:
                        await self.execute_exit(sym, pos['qty'], f"🌾 HARVESTER TRAIL EXIT (Slot {pos['slot']}, Peak: {pos['peak_profit']*100:.1f}%)")
                    # Hard stop loss at -1.5%
                    elif profit_pct <= -self.STOP_LOSS_PCT:
                        await self.execute_exit(sym, pos['qty'], f"🛡️ HARVESTER STOP (Slot {pos['slot']})")
                        
        except ccxt.RateLimitExceeded:
            self._log("⚠️ RATE LIMIT: Activating adaptive throttle")
            self.current_pulse = 4
            self.pulse_reset_time = time.time() + 60
        except Exception as e:
            self._log(f"⚠️ MONITOR ERROR: {e}")

    async def execute_exit(self, symbol, qty, reason):
        try:
            await self.exchange.create_market_sell_order(symbol, qty)
            self._log(f"{reason}: {symbol} Closed.")
            del self.active_slots[symbol]
        except ccxt.ExchangeError as e:
            # Sync-Guard: Handle error 30005 (Oversold - exchange already closed position)
            error_str = str(e)
            if '30005' in error_str:
                self._log(f"🛡️ SYNC-GUARD: Slot forced clear (Exchange side closed) - {symbol}")
                # Force clear the slot since exchange already closed it
                if symbol in self.active_slots:
                    del self.active_slots[symbol]
            else:
                self._log(f"❌ EXIT FAILED: {e}")
        except Exception as e:
            self._log(f"❌ EXIT FAILED: {e}")

    def _log(self, msg: str) -> None:
        logger.info(msg)

    async def start(self):
        self._log("🛡️ T.I.A. HYBRID SWARM: SYNC-GUARD ARMED & STABILIZED")
        self._log(f"🦈 PIRANHA: Green candles → 0.4% exits")
        self._log(f"🌾 HARVESTER: Top movers → Trailing 0.5% grid")
        self._log(f"🛡️ SYNC-GUARD: 5s cooldown + Error 30005/10007 protection")
        
        while True:
            # Check if pulse needs to be reset
            if self.pulse_reset_time and time.time() >= self.pulse_reset_time:
                self.current_pulse = 2
                self.pulse_reset_time = None
                self._log("✅ PULSE RESET: Back to 2s scan interval")
            
            await self.scout_and_buy()
            await self.pulse_monitor()
            await asyncio.sleep(self.current_pulse)

# CRITICAL ALIAS for FastAPI Compatibility
VortexEngine = VortexBerserker

if __name__ == "__main__":
    vortex = VortexBerserker()
    asyncio.run(vortex.start())
