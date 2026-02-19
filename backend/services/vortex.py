import asyncio, os, logging, json, time
import ccxt.async_support as ccxt
import pandas as pd
import pandas_ta as ta

# T.I.A. TOTALITY HUD
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [OPERATOR] - %(message)s')
logger = logging.getLogger("vortex")

class VortexTotality:
    def __init__(self):
        self.stake = 10.00
        self.max_slots = 16
        self.active_trades = {}
        self.mlofi_threshold = 0.08
        self.bible_path = "/content/drive/MyDrive/pioneer-trader/Codex/vortex.py"
        self.exchange = ccxt.mexc({
            'apiKey': os.getenv('MEXC_API_KEY'), 
            'secret': os.getenv('MEXC_SECRET'), 
            'options': {'createMarketBuyOrderRequiresPrice': False}
        })

    async def get_mlofi(self, symbol):
        """District 05: Institutional Radar"""
        try:
            ob = await self.exchange.fetch_order_book(symbol, limit=10)
            bids = sum([v for p, v in ob['bids'][:5]])
            asks = sum([v for p, v in ob['asks'][:5]])
            return (bids - asks) / (bids + asks)
        except: return -1

    async def apply_library(self, symbol, df):
        """The 22-Strategy Hive Mind"""
        last = df.iloc[-1]; rsi = ta.rsi(df['c']).iloc[-1]
        ema50 = ta.ema(df['c'], length=50).iloc[-1]
        bb = ta.bbands(df['c']); bbl = bb['BBL_5_2.0'].iloc[-1]
        
        # Aggressive Logic Selection
        if symbol == "XRP/USDT" and last['c'] < 1.43: return "XRP_FLOOR"
        if rsi < 25 and last['c'] > ema50: return "P25_SNIPER"
        if last['c'] < bbl: return "CRAB_REVERSION"
        if rsi < 35: return "PIRANHA_SCALP"
        return None

    async def start(self):
        logger.info("🔥 OMEGA IGNITION: 16 SLOTS LIVE. TARGETING $160 -> $320.")
        await self.exchange.load_markets()
        
        while True:
            try:
                # 1. SCAN THE TOP 50 VOLUMETRIC TARGETS
                tickers = await self.exchange.fetch_tickers()
                targets = [s for s, t in tickers.items() if '/USDT' in s and t['quoteVolume'] > 2000000]
                targets.sort(key=lambda x: tickers[x]['percentage'], reverse=False)

                # 2. MANAGE THE FLEET (Exits)
                for sym in list(self.active_trades.keys()):
                    trade = self.active_trades[sym]
                    ticker = await self.exchange.fetch_ticker(sym)
                    pnl = (ticker['last'] - trade['entry']) / trade['entry']
                    
                    if pnl >= 0.03 or pnl <= -0.015: # Aggressive 3% TP / 1.5% SL
                        await self.exchange.create_market_sell_order(sym, trade['qty'])
                        logger.info(f"💰 BANKED {sym}: {pnl*100:.2f}%")
                        del self.active_trades[sym]

                # 3. EXECUTE STRIKES (Entries)
                if len(self.active_trades) < self.max_slots:
                    for pair in targets[:30]:
                        if pair in self.active_trades: continue
                        ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='5m', limit=50)
                        df = pd.DataFrame(ohlcv, columns=['t','o','h','l','c','v'])
                        
                        signal = await self.apply_library(pair, df)
                        if signal and await self.get_mlofi(pair) > self.mlofi_threshold:
                            order = await self.exchange.create_market_buy_order(pair, self.stake)
                            self.active_trades[pair] = {'entry': order['price'], 'qty': order['filled'], 'wing': signal}
                            logger.info(f"🚀 {signal} STRIKE: {pair} - $10 Commit.")
                            break
            except Exception as e: logger.error(f"💀 FRACTURE: {e}")
            await asyncio.sleep(15)

VortexEngine = VortexTotality
