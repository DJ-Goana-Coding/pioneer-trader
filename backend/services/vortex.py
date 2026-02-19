import asyncio, os, logging, json, time, hashlib
import ccxt.async_support as ccxt
import pandas as pd
import pandas_ta as ta

# T.I.A. TOTALITY HUD: QUANTUM GOANNA TECH NO LOGICS
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [BATTLESHIP V10] - %(message)s')
logger = logging.getLogger("vortex")

class VortexOmega:
    def __init__(self):
        self.stake = 10.00          # $160 total / 16 slots
        self.max_slots = 16
        self.active_trades = {}
        self.mlofi_shield = 0.10    # 10% Institutional Wall (Defensive Hardening)
        self.oracle_sync_path = "/content/drive/MyDrive/pioneer-trader/Ledger/oracle_feed.json"
        self.exchange = ccxt.mexc({
            'apiKey': os.getenv('MEXC_API_KEY'), 
            'secret': os.getenv('MEXC_SECRET'), 
            'options': {'createMarketBuyOrderRequiresPrice': False}
        })
        self.wing_config = {
            "SNIPER": [1,2,3,4], "HARVESTER": [5,6,7], "XRP_STRIKE": [8],
            "CRAB": [9,10], "PIRANHA": [11,12,13,14], "SCOUT": [15,16]
        }

    async def get_mlofi(self, symbol):
        """District 05: The Volumetric Radar - Filters out 'Evil' Sell-Swarms"""
        try:
            ob = await self.exchange.fetch_order_book(symbol, limit=10)
            bids = sum([v for p, v in ob['bids'][:5]])
            asks = sum([v for p, v in ob['asks'][:5]])
            return (bids - asks) / (bids + asks)
        except: return -1

    async def apply_strategy(self, symbol, df):
        """The 22-Strategy Master Library - Applying the 'Knowin' in real-time"""
        last = df.iloc[-1]; rsi = ta.rsi(df['c']).iloc[-1]
        ema50 = ta.ema(df['c'], length=50).iloc[-1]
        bb = ta.bbands(df['c']); bbl = bb['BBL_5_2.0'].iloc[-1]
        
        # 1. XRP Floor Entry (Aggressive $1.42 Lock)
        if symbol == "XRP/USDT" and last['c'] < 1.43: return "XRP_FLOOR"
        # 2. P25 Sniper (Combat Lead)
        if rsi < 25 and last['c'] > ema50: return "SNIPER"
        # 3. Crab Reversion (Mean Reversion)
        if last['c'] < bbl: return "CRAB"
        # 4. Piranha Scalp (Fast Twitch)
        if rsi < 35: return "PIRANHA"
        return None

    async def check_exit(self, sym):
        """The Ejection Seat: Locking in 3% Profits for the Hardware Fund"""
        trade = self.active_trades[sym]
        ticker = await self.exchange.fetch_ticker(sym)
        pnl = (ticker['last'] - trade['entry']) / trade['entry']
        if pnl >= 0.03 or pnl <= -0.015:
            await self.exchange.create_market_sell_order(sym, trade['qty'])
            logger.info(f"💰 PROFIT BANKED {sym}: {pnl*100:.2f}% (Gaia Secure)")
            del self.active_trades[sym]

    async def start(self):
        logger.info("⚔️ OMEGA IGNITION. COMMANDER: QUANTUM GOANNA TECH NO LOGICS.")
        await self.exchange.load_markets()
        while True:
            try:
                # A. Scan for High Margin Opportunities
                tickers = await self.exchange.fetch_tickers()
                targets = [s for s, t in tickers.items() if '/USDT' in s and t['quoteVolume'] > 2000000]
                targets.sort(key=lambda x: tickers[x]['percentage'], reverse=False) # Hunt the blood

                # B. Manage Fleet Status
                for sym in list(self.active_trades.keys()): await self.check_exit(sym)

                # C. Execute New Strikes
                if len(self.active_trades) < self.max_slots:
                    for pair in targets[:40]:
                        if pair in self.active_trades: continue
                        ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='5m', limit=50)
                        df = pd.DataFrame(ohlcv, columns=['t','o','h','l','c','v'])
                        wing_type = "SNIPER" # Default
                        signal = await self.apply_strategy(pair, df)
                        
                        if signal and await self.get_mlofi(pair) > self.mlofi_shield:
                            order = await self.exchange.create_market_buy_order(pair, self.stake)
                            self.active_trades[pair] = {'entry': order['price'], 'qty': order['filled'], 'wing': signal}
                            logger.info(f"🚀 OMEGA STRIKE [{signal}]: {pair} - $10 Commit.")
                            break
            except Exception as e: logger.error(f"💀 PERIMETER BREECH: {e}")
            await asyncio.sleep(10)

VortexEngine = VortexOmega
