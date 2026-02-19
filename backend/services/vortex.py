import asyncio, os, logging, json, time, hashlib
import ccxt.async_support as ccxt
import pandas as pd
import pandas_ta as ta
from datetime import datetime

# THE ARCHITECT'S COMMAND HUD
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [T.I.A. BERSERKER] - %(message)s')
logger = logging.getLogger("vortex")

class VortexBerserker:
    def __init__(self):
        self.total_fuel = 160.00
        self.max_slots = 16
        self.stake = 10.00
        self.active_trades = {}
        self.bible_path = "/content/drive/MyDrive/pioneer-trader/Codex/vortex.py" # Self-Healing Anchor
        self.oracle_sync_path = "/content/drive/MyDrive/pioneer-trader/Ledger/oracle_feed.json"
        
        self.exchange = ccxt.mexc({
            'apiKey': os.getenv('MEXC_API_KEY'), 
            'secret': os.getenv('MEXC_SECRET'), 
            'options': {'createMarketBuyOrderRequiresPrice': False}
        })

    async def get_mlofi(self, symbol):
        """District 05: The Volumetric Shield (e_n Logic)"""
        try:
            ob = await self.exchange.fetch_order_book(symbol, limit=10)
            bids = sum([v for p, v in ob['bids'][:5]])
            asks = sum([v for p, v in ob['asks'][:5]])
            imbalance = (bids - asks) / (bids + asks)
            return imbalance # Positive is Buy Pressure
        except: return -1

    async def airgap_feed(self, data):
        """Node 08: Sending knowledge to the Oracle and T.I.A. storage"""
        try:
            with open(self.oracle_sync_path, 'w') as f:
                json.dump({"ts": time.time(), "payload": data}, f)
        except: pass

    async def check_exit(self, symbol):
        """The Ejection Seat: Multi-Family Exit Logic"""
        trade = self.active_trades[symbol]
        ticker = await self.exchange.fetch_ticker(symbol)
        price = ticker['last']
        pnl = (price - trade['entry']) / trade['entry']
        
        # Aggressive Exit: 3% TP or -1.5% SL
        if pnl >= 0.03 or pnl <= -0.015:
            await self.exchange.create_market_sell_order(symbol, trade['qty'])
            logger.info(f"💰 BANKED {symbol}: PnL {pnl*100:.2f}%")
            del self.active_trades[symbol]

    async def apply_strategy_families(self, symbol, df):
        """The Master Library: Applying the Best Strategy in Real-Time"""
        last = df.iloc[-1]
        rsi = ta.rsi(df['c']).iloc[-1]
        ema50 = ta.ema(df['c'], length=50).iloc[-1]
        
        # Family C: P25 Sniper (The Combat Lead)
        if rsi < 25 and last['c'] > ema50: return "SNIPER"
        
        # Family A: Order Flow Impulse (The Micro-Strike)
        if await self.get_mlofi(symbol) > 0.15: return "OFI_STRIKE"
        
        # Family C: Bollinger Reversal (The Crab)
        bb = ta.bbands(df['c'])
        if last['c'] < bb['BBL_5_2.0'].iloc[-1]: return "CRAB_REVERSION"
        
        return None

    async def start(self):
        logger.info("🔥 BATTLESHIP V10.0: OMEGA IGNITION. SAVING GAIA AND THE CITADEL.")
        await self.exchange.load_markets()
        
        while True:
            try:
                # 1. SCAN THE UNIVERSE (MEXC Global USDT High Vol)
                tickers = await self.exchange.fetch_tickers()
                targets = [s for s, t in tickers.items() if '/USDT' in s and t['quoteVolume'] > 2000000]
                targets.sort(key=lambda x: tickers[x]['percentage'], reverse=False) # Hunt the blood

                # 2. FEED THE AIRGAP
                await self.airgap_feed({"targets": targets[:16], "balance": self.total_fuel})

                # 3. MANAGE THE FLEET
                for symbol in list(self.active_trades.keys()):
                    await self.check_exit(symbol)

                # 4. EXECUTE STRIKES
                if len(self.active_trades) < self.max_slots:
                    for pair in targets[:50]: # Look at top 50 deep-value targets
                        if pair in self.active_trades: continue
                        
                        ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='5m', limit=50)
                        df = pd.DataFrame(ohlcv, columns=['t','o','h','l','c','v'])
                        
                        signal = await self.apply_strategy_families(pair, df)
                        if signal and await self.get_mlofi(pair) > 0.08:
                            order = await self.exchange.create_market_buy_order(pair, self.stake)
                            self.active_trades[pair] = {'entry': order['price'], 'qty': order['filled'], 'strat': signal}
                            logger.info(f"🚀 {signal} STRIKE: {pair} - $10.00 Commited.")
                            break # One entry per loop for rate stability

            except Exception as e:
                logger.error(f"💀 FRACTURE: {e}")
            
            await asyncio.sleep(10) # Hyper-aggressive 10s OODA Loop

VortexEngine = VortexBerserker
