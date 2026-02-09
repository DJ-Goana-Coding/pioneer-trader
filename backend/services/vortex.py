import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import pandas_ta as ta
import os
import json
import time
from datetime import datetime
from huggingface_hub import HfApi
from backend.core.logging_config import setup_logging

# Setup Logger
logger = setup_logging("vortex")

class VortexBerserker:
    def __init__(self):
        # 1. FLEET CONFIGURATION (2/4/1 Split)
        self.PIRANHA_SLOTS = [1, 2]       # 0.4% Scalps
        self.HARVESTER_SLOTS = [3, 4, 5, 6] # Trailing Grids
        self.SNIPER_SLOT = [7]            # EMA50 + Vol Surge
        
        # 2. EXCHANGE & SECURITY
        self.api_key = os.getenv("MEXC_API_KEY")
        self.secret = os.getenv("MEXC_SECRET")
        self.mexc = ccxt.mexc({
            'apiKey': self.api_key, 'secret': self.secret, 
            'enableRateLimit': True, 'options': {'defaultType': 'spot'}
        })
        self.blacklisted = set(['PENGUIN/USDT']) # Perimeter Guard
        
        # 3. STATE & UPLINKS
        self.active_trades = {}
        self.hf_api = HfApi()
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        self.hf_repo = os.getenv("HUGGINGFACE_REPO")
        self.shadow_path = os.getenv("SHADOW_ARCHIVE_PATH", "/tmp/airgap")
        self.running = False
        self.base_stake = 8.00
        
        # 4. LEGACY COMPATIBILITY
        self.exchange = self.mexc  # Alias for compatibility
        self.active_slots = self.active_trades  # Alias for compatibility
        self.blacklisted_symbols = self.blacklisted  # Alias for compatibility
        self.max_slots = 7
        self.current_pulse = 2  # Adaptive pulse: 2s default, 4s on rate limit
        self.pulse_reset_time = None  # Track when to reset pulse
        
        # Trading Parameters (for compatibility)
        self.PIRANHA_PROFIT_TARGET = 0.004  # 0.4% fixed profit exit
        self.HARVESTER_TRAIL_START = 0.005  # 0.5% profit to start trailing
        self.HARVESTER_PULLBACK_EXIT = 0.015  # 1.5% pullback from peak to exit
        self.STOP_LOSS_PCT = 0.015  # 1.5% hard stop loss
        self.stop_loss_pct = self.STOP_LOSS_PCT
        self.POST_BUY_COOLDOWN = 5.0  # 5-second cooldown after buy before allowing sell

    async def _scan_market(self):
        """Dual-Scan: Momentum for Piranhas, EMA/Vol for Sniper"""
        try:
            tickers = await self.mexc.fetch_tickers()
            candidates = []
            sniper_targets = []
            
            for s, t in tickers.items():
                if '/USDT' in s and t.get('quoteVolume', 0) > 500000 and s not in self.blacklisted:
                    # Basic Piranha/Harvester Filter
                    if t.get('percentage', 0) > 2.0 and t.get('last', 0) > t.get('open', 0):
                        candidates.append({'symbol': s, 'price': t['last'], 'change': t['percentage']})
                    
                    # Sniper Filter (Heavy Compute - Limit to Top 10 Vol)
                    # Note: In prod, we fetch OHLCV only for high-potential targets
                    # This is a simplified logic for the 2s pulse
                    if t.get('percentage', 0) > 5.0 and t.get('quoteVolume', 0) > 5000000:
                        sniper_targets.append(s)

            return sorted(candidates, key=lambda x: x['change'], reverse=True), sniper_targets
        except ccxt.RateLimitExceeded:
            self._log("⚠️ RATE LIMIT: Activating adaptive throttle")
            self.current_pulse = 4
            self.pulse_reset_time = time.time() + 60
            return [], []
        except Exception as e:
            self._log(f"⚠️ SCAN ERROR: {e}")
            return [], []

    async def _analyze_sniper(self, symbol):
        """🦅 SNIPER LOGIC: EMA50 + 300% Vol Surge"""
        try:
            ohlcv = await self.mexc.fetch_ohlcv(symbol, '5m', limit=55)
            df = pd.DataFrame(ohlcv, columns=['time','open','high','low','close','vol'])
            
            # Technicals
            df['ema50'] = ta.ema(df['close'], length=50)
            avg_vol = df['vol'].iloc[-20:].mean()
            curr_vol = df['vol'].iloc[-1]
            curr_price = df['close'].iloc[-1]
            ema_price = df['ema50'].iloc[-1]

            # The Kill-Shot Condition
            if curr_price > ema_price and curr_vol > (avg_vol * 3):
                return True
            return False
        except Exception as e:
            # Check for error code 10007 (invalid symbol)
            error_str = str(e)
            if '10007' in error_str:
                self.blacklisted.add(symbol)
                self._log(f"🚫 BLACKLIST: {symbol} (Error 10007 - Invalid symbol)")
            return False

    def get_available_slot_type(self):
        """Determine which wing has available slots."""
        occupied_slots = [pos.get('slot') for pos in self.active_trades.values()]
        
        # Check Piranha slots (1-2)
        for slot in self.PIRANHA_SLOTS:
            if slot not in occupied_slots:
                return ('piranha', slot)
        
        # Check Harvester slots (3-6)
        for slot in self.HARVESTER_SLOTS:
            if slot not in occupied_slots:
                return ('harvester', slot)
        
        # Check Sniper slot (7)
        for slot in self.SNIPER_SLOT:
            if slot not in occupied_slots:
                return ('sniper', slot)
        
        return (None, None)
    
    async def scout_and_buy(self):
        """Hybrid Swarm Scanner with Sniper Logic."""
        if len(self.active_trades) >= self.max_slots: 
            return

        try:
            # Scan market for candidates and sniper targets
            movers, potential_snipers = await self._scan_market()
            if not movers and not potential_snipers:
                return
            
            # Check Sniper Slot (7) - highest priority
            if 7 not in self.active_trades and potential_snipers:
                for target in potential_snipers[:3]:  # Check top 3
                    if await self._analyze_sniper(target):
                        await self._fill_slot(7, target, "sniper")
                        return  # One entry per cycle
            
            # Fill Piranha/Harvester slots
            for m in movers:
                if len(self.active_trades) >= 7:
                    break
                # Find empty slot
                empty_slots = [i for i in range(1, 7) if i not in self.active_trades]
                if empty_slots:
                    slot = empty_slots[0]
                    w = "piranha" if slot in self.PIRANHA_SLOTS else "harvester"
                    if m['symbol'] not in [t['symbol'] for t in self.active_trades.values()]:
                        await self._fill_slot(slot, m['symbol'], w, m['price'])
                        return  # One entry per cycle
                        
        except ccxt.RateLimitExceeded:
            self._log("⚠️ RATE LIMIT: Activating adaptive throttle")
            self.current_pulse = 4
            self.pulse_reset_time = time.time() + 60
        except Exception as e:
            self._log(f"⚠️ SCAN ERROR: {e}")

    async def _fill_slot(self, slot, symbol, wing, price=None):
        """Fill a trading slot with a new position."""
        if not price:
            try:
                ticker = await self.mexc.fetch_ticker(symbol)
                price = ticker['last']
            except Exception as e:
                self._log(f"⚠️ PRICE FETCH ERROR {symbol}: {e}")
                return
        
        try:
            # Calculate exact amount (Base Currency)
            amount = self.base_stake / price
            order = await self.mexc.create_market_buy_order(symbol, amount)
            
            wing_emoji = "🦈" if wing == 'piranha' else ("🌾" if wing == 'harvester' else "🎯")
            self._log(f"⚔️ {wing.upper()} (Slot {slot}) attacking {symbol} @ {price}")
            
            self.active_trades[slot] = {
                'symbol': symbol, 
                'entry': price, 
                'peak': price, 
                'wing': wing,
                'start_time': datetime.now().isoformat(),
                'qty': amount,
                'time': time.time(),
                'slot': slot,
                'peak_profit': 0.0
            }
        except Exception as e:
            error_str = str(e)
            if "10007" in error_str:
                self._log(f"🛡️ PERIMETER: Blacklisting {symbol} (API Blocked)")
                self.blacklisted.add(symbol)
            else:
                self._log(f"❌ BUY FAILED: {e}")

    async def pulse_monitor(self):
        """Hybrid Exit Logic: Piranha (0.4% fixed) vs Harvester (trailing grid) vs Sniper (1.5% fixed)."""
        await self._manage_exits()
    
    async def _manage_exits(self):
        """Monitor and exit positions based on wing-specific strategies."""
        if not self.active_trades: 
            return
        
        try:
            # Get current prices for all active positions
            symbols_list = [trade['symbol'] for trade in self.active_trades.values()]
            tickers = await self.mexc.fetch_tickers(symbols_list)
            
            for slot, trade in list(self.active_trades.items()):
                # Sync-Guard: Enforce post-buy cooldown (5 seconds)
                time_held = time.time() - trade['time']
                if time_held < self.POST_BUY_COOLDOWN:
                    logger.debug(f"⏳ Cooldown active: {trade['symbol']} held for {time_held:.1f}s/{self.POST_BUY_COOLDOWN}s")
                    continue  # Skip this slot until cooldown expires
                
                curr = tickers[trade['symbol']]['last']
                profit_pct = (curr - trade['entry']) / trade['entry']
                
                # SNIPER: Fixed 1.5% TP / 1.5% SL
                if trade['wing'] == "sniper":
                    if curr >= trade['entry'] * 1.015:
                        await self._execute_sell(slot, trade, "🎯 SNIPER HEADSHOT")
                    elif curr <= trade['entry'] * 0.985:
                        await self._execute_sell(slot, trade, "💀 SNIPER MISS")

                # PIRANHA: 0.4% Scalp
                elif trade['wing'] == "piranha":
                    if profit_pct >= self.PIRANHA_PROFIT_TARGET:
                        await self._execute_sell(slot, trade, f"💰 PIRANHA BITE (Slot {slot})")
                    elif profit_pct <= -self.STOP_LOSS_PCT:
                        await self._execute_sell(slot, trade, f"🛡️ PIRANHA STOP (Slot {slot})")
                
                # HARVESTER: Trailing Grid
                elif trade['wing'] == "harvester":
                    # Update peak profit
                    if profit_pct > trade['peak_profit']:
                        old_peak = trade['peak_profit']
                        trade['peak_profit'] = profit_pct
                        # Log only significant trailing activations
                        if profit_pct >= self.HARVESTER_TRAIL_START and (old_peak == 0 or profit_pct - old_peak >= 0.005):
                            self._log(f"📈 HARVESTER TRAILING: {trade['symbol']} Peak: {trade['peak_profit']*100:.2f}%")
                    
                    # Exit on 1.5% pullback from peak
                    pullback = trade['peak_profit'] - profit_pct
                    if trade['peak_profit'] > 0 and pullback >= self.HARVESTER_PULLBACK_EXIT:
                        await self._execute_sell(slot, trade, f"🌾 HARVEST DONE (Slot {slot}, Peak: {trade['peak_profit']*100:.1f}%)")
                    # Hard stop loss
                    elif profit_pct <= -self.STOP_LOSS_PCT:
                        await self._execute_sell(slot, trade, f"🛡️ HARVESTER STOP (Slot {slot})")
                        
        except ccxt.RateLimitExceeded:
            self._log("⚠️ RATE LIMIT: Activating adaptive throttle")
            self.current_pulse = 4
            self.pulse_reset_time = time.time() + 60
        except Exception as e:
            self._log(f"⚠️ MONITOR ERROR: {e}")

    async def _execute_sell(self, slot, trade, reason):
        """Execute sell order with Sync-Guard protection."""
        try:
            # BALANCE CHECK (Sync-Guard)
            bal = await self.mexc.fetch_balance()
            coin = trade['symbol'].split('/')[0]
            if bal.get(coin, {}).get('free', 0) > 0:
                await self.mexc.create_market_sell_order(trade['symbol'], trade['qty'])
                self._log(f"{reason}: {trade['symbol']} Closed.")
                
                # DATA UPLINK TRIGGER
                self._uplink_data(trade)
            else:
                self._log(f"🛡️ SYNC-GUARD: Ghost slot cleared {trade['symbol']}")
            
            del self.active_trades[slot]
        except ccxt.ExchangeError as e:
            # Sync-Guard: Handle error 30005 (Oversold - exchange already closed position)
            error_str = str(e)
            if '30005' in error_str:
                self._log(f"🛡️ SYNC-GUARD: Error 30005 detected - {trade['symbol']}")
                
                # Extract coin symbol
                coin_symbol = trade['symbol'].split('/')[0] if '/' in trade['symbol'] else trade['symbol']
                
                # Check balance before clearing slot
                try:
                    balance = await self.mexc.fetch_balance()
                    free_balance = balance.get(coin_symbol, {}).get('free', 0)
                    
                    if free_balance > 0:
                        # Final attempt to sell if balance exists
                        self._log(f"🛡️ SYNC-GUARD: Balance detected ({free_balance} {coin_symbol}), attempting force exit")
                        await self.force_exit(trade['symbol'], free_balance)
                    else:
                        self._log(f"🛡️ SYNC-GUARD: Balance confirmed at 0, clearing slot - {trade['symbol']}")
                except Exception as balance_err:
                    self._log(f"⚠️ SYNC-GUARD: Balance check failed - {balance_err}")
                
                # Clear the slot after balance verification
                if slot in self.active_trades:
                    del self.active_trades[slot]
            else:
                self._log(f"❌ EXIT FAILED: {e}")
        except Exception as e:
            self._log(f"❌ EXIT FAILED: {e}")
    
    async def force_exit(self, symbol, qty):
        """Force exit a position - final attempt to sell remaining balance."""
        try:
            await self.mexc.create_market_sell_order(symbol, qty)
            self._log(f"🛡️ FORCE EXIT SUCCESS: {symbol} ({qty})")
        except Exception as e:
            self._log(f"⚠️ FORCE EXIT FAILED: {symbol} - {e}")

    def _uplink_data(self, trade_data):
        """Push to Airgap and Hugging Face"""
        # 1. AIRGAP DUMP
        try:
            os.makedirs(self.shadow_path, exist_ok=True)
            with open(f"{self.shadow_path}/trades.jsonl", "a") as f:
                f.write(json.dumps(trade_data) + "\n")
        except Exception as e:
            logger.debug(f"Airgap write failed: {e}")
        
        # 2. HUGGING FACE PUSH (Async wrapper needed in prod)
        if self.hf_token and self.hf_repo:
            try:
                # Create a temporary file for upload
                temp_data = json.dumps(trade_data).encode()
                import tempfile
                with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.json') as tmp:
                    tmp.write(temp_data)
                    tmp_path = tmp.name
                
                self.hf_api.upload_file(
                    path_or_fileobj=tmp_path,
                    path_in_repo=f"trades/{datetime.now().timestamp()}.json",
                    repo_id=self.hf_repo,
                    token=self.hf_token
                )
                
                # Clean up temp file
                os.unlink(tmp_path)
            except Exception as e:
                logger.debug(f"⚠️ UPLINK FAIL: {e}")

    def _log(self, msg: str) -> None:
        """Log with T.I.A. signature prefix."""
        formatted = f"[T.I.A.] {msg}"
        logger.info(formatted)

    async def start(self):
        """Start the Vortex V2 trading engine."""
        self._log("🔥 VORTEX V2: 2 PIRANHAS // 4 HARVESTERS // 1 SNIPER")
        self._log(f"📡 UPLINKS: HF={bool(self.hf_token)} | AIRGAP={self.shadow_path}")
        self._log(f"🦈 PIRANHA (Slots 1-2): 0.4% scalps")
        self._log(f"🌾 HARVESTER (Slots 3-6): Trailing 0.5% grid")
        self._log(f"🎯 SNIPER (Slot 7): EMA50 + 3x Vol surge → 1.5% TP/SL")
        self._log(f"🛡️ SYNC-GUARD: 5s cooldown + Error 30005/10007 protection")
        self.running = True
        
        while self.running:
            # Check if pulse needs to be reset
            if self.pulse_reset_time and time.time() >= self.pulse_reset_time:
                self.current_pulse = 2
                self.pulse_reset_time = None
                self._log("✅ PULSE RESET: Back to 2s scan interval")
            
            await self.scout_and_buy()
            await self.pulse_monitor()
            await asyncio.sleep(self.current_pulse)
    
    # Legacy compatibility methods
    async def fetch_global_market(self):
        """Legacy compatibility: returns candidates only."""
        candidates, _ = await self._scan_market()
        return candidates
    
    async def get_candle_data(self, symbol: str):
        """Legacy compatibility: fetch 1-minute candle data."""
        try:
            ohlcv = await self.mexc.fetch_ohlcv(symbol, timeframe='1m', limit=2)
            if len(ohlcv) < 2:
                return None
            df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
            return df
        except Exception as e:
            error_str = str(e)
            if '10007' in error_str:
                self.blacklisted.add(symbol)
                self._log(f"🚫 BLACKLIST: {symbol} (Error 10007 - Invalid symbol)")
            return None
    
    async def execute_order(self, symbol, price, wing_type, slot_num):
        """Legacy compatibility: execute order."""
        await self._fill_slot(slot_num, symbol, wing_type, price)
    
    async def execute_exit(self, symbol, qty, reason):
        """Legacy compatibility: execute exit by symbol."""
        # Find the slot for this symbol
        slot = None
        for s, trade in self.active_trades.items():
            if trade['symbol'] == symbol:
                slot = s
                break
        
        if slot:
            await self._execute_sell(slot, self.active_trades[slot], reason)

# CRITICAL ALIAS for FastAPI Compatibility
VortexEngine = VortexBerserker

if __name__ == "__main__":
    vortex = VortexBerserker()
    asyncio.run(vortex.start())
