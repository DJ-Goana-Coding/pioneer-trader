import os, asyncio, ccxt.async_support as ccxt
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import time

class VortexBerserker:
    def __init__(self):
        self.base_stake = 8.00 
        self.max_slots = 7
        self.stop_loss_pct = 0.015
        self.universe = ['SOL/USDT', 'XRP/USDT', 'DOGE/USDT', 'ADA/USDT', 'PEPE/USDT']
        self.active_slots = {} 
        self.exchange = None
        self._init_mexc()

    def _init_mexc(self):
        """Live Connection to MEXC."""
        self.exchange = ccxt.mexc({
            'apiKey': os.getenv('MEXC_API_KEY'),
            'secret': os.getenv('MEXC_SECRET'),
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })

    async def get_indicators(self, symbol):
        """Technical Analysis: The Eyes."""
        ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe='1m', limit=50)
        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
        rsi = ta.rsi(df['close'], length=14).iloc[-1]
        ema50 = ta.ema(df['close'], length=50).iloc[-1]
        return rsi, ema50, df['close'].iloc[-1]

    async def scout_and_buy(self):
        """The Sniper: Scans for RSI < 40 setups."""
        if len(self.active_slots) >= self.max_slots: 
            return

        for symbol in self.universe:
            if symbol in self.active_slots: 
                continue
            
            try:
                rsi, ema50, price = await self.get_indicators(symbol)
                
                # STRATEGY: BUY if Oversold (RSI < 40) AND Uptrend (Price > EMA50)
                if rsi < 40 and price > ema50:
                    self._log(f"⚔️ SIGNAL: {symbol} (RSI: {rsi:.1f})")
                    await self.execute_order(symbol, price)
                    
            except Exception as e:
                self._log(f"⚠️ SCAN ERROR {symbol}: {e}")

    async def execute_order(self, symbol, price):
        try:
            # Calculate exact amount (Base Currency)
            amount = self.base_stake / price
            order = await self.exchange.create_market_buy_order(symbol, amount)
            self.active_slots[symbol] = {'entry': price, 'qty': amount, 'time': time.time()}
            self._log(f"🔥 FILLED: {symbol} @ ${price:.4f}")
        except Exception as e:
            self._log(f"❌ BUY FAILED: {e}")

    async def pulse_monitor(self):
        """The Ejector Seat: 1.5% Hard Stop."""
        if not self.active_slots: 
            return
        
        tickers = await self.exchange.fetch_tickers(list(self.active_slots.keys()))
        for sym, pos in list(self.active_slots.items()):
            curr_price = tickers[sym]['last']
            loss = (pos['entry'] - curr_price) / pos['entry']
            
            # STOP LOSS (1.5%)
            if loss >= self.stop_loss_pct:
                await self.execute_exit(sym, pos['qty'], "🛡️ STOP LOSS")
            
            # TAKE PROFIT (Quick Scalp 1.5%)
            elif (curr_price - pos['entry']) / pos['entry'] > 0.015:
                await self.execute_exit(sym, pos['qty'], "💰 PROFIT")

    async def execute_exit(self, symbol, qty, reason):
        try:
            await self.exchange.create_market_sell_order(symbol, qty)
            self._log(f"{reason}: {symbol} Closed.")
            del self.active_slots[symbol]
        except Exception as e:
            self._log(f"❌ EXIT FAILED: {e}")

    def _log(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    async def start(self):
        self._log("🏰 CITADEL V6.9: LIVE FIRE ENGAGED.")
        self._log(f"⚔️ SNIPER MODE: RSI<40 + Price>EMA50 | 🛡️ STOP: {self.stop_loss_pct*100}%")
        while True:
            await self.scout_and_buy()
            await self.pulse_monitor()
            await asyncio.sleep(8)

# CRITICAL ALIAS for FastAPI Compatibility
VortexEngine = VortexBerserker

if __name__ == '__main__':
    vortex = VortexBerserker()
    asyncio.run(vortex.start())