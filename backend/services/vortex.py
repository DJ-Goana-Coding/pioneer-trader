import asyncio, os, logging, json, time
import ccxt.async_support as ccxt
import pandas as pd
import pandas_ta as ta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [BATTLESHIP V10] - %(message)s')
logger = logging.getLogger("vortex")

class VortexOmega:
    def __init__(self):
        self.stake = 10.00          
        self.max_slots = 16
        self.active_trades = {}
        self.mlofi_shield = 0.10    
        # Oracle Sovereign Cloud Data Path
        self.oracle_sync_path = "oracle_feed.json" 
        self.exchange = ccxt.mexc({
            'apiKey': os.getenv('MEXC_API_KEY'), 
            'secret': os.getenv('MEXC_SECRET'), 
            'options': {'createMarketBuyOrderRequiresPrice': False}
        })

    async def get_mlofi(self, symbol):
        """District 05: The Volumetric Radar"""
        try:
            ob = await self.exchange.fetch_order_book(symbol, limit=10)
            bids = sum([v for p, v in ob['bids'][:5]])
            asks = sum([v for p, v in ob['asks'][:5]])
            return (bids - asks) / (bids + asks)
        except: return -1

    async def apply_strategy(self, symbol, df, slot_index):
        """T.I.A. Feathered Logic: Diversity across 16 slots"""
        last = df.iloc[-1]
        rsi = ta.rsi(df['c']).iloc[-1]
        ema50 = ta.ema(df['c'], length=50).iloc[-1]
        bb = ta.bbands(df['c'])
        bbl = bb['BBL_5_2.0'].iloc[-1]
        
        # 1. FIXED ASSET STRIKE (XRP Floor)
        if symbol == "XRP/USDT" and last['c'] < 1.43: return "XRP_STRIKE"
        
        # 2. BERSERKER WICK CATCH (Slots 13-16: High Aggression)
        if slot_index >= 12:
            if rsi < 20 or last['c'] < (bbl * 0.98): return "BERSERKER"
            
        # 3. RAIDER REVERSION (Slots 8-12: Mid Aggression)
        elif slot_index >= 8:
            if last['c'] < bbl: return "RAIDER"
            
        # 4. SNIPER/PIRANHA (Slots 0-7: Conservative)
        else:
            if rsi < 25 and last['c'] > ema50: return "SNIPER"
            if rsi < 35: return "PIRANHA"
            
        return None

    async def check_exit(self, sym):
        """District 01: Profit Realization"""
        trade = self.active_trades[sym]
        ticker = await self.exchange.fetch_ticker(sym)
        pnl = (ticker['last'] - trade['entry']) / trade['entry']
        
        # Exit at 3% Profit or 1.5% Stop Loss
        if pnl >= 0.03 or pnl <= -0.015:
            await self.exchange.create_market_sell_order(sym, trade['qty'])
            logger.info(f"💰 BANKED {sym}: {pnl*100:.2f}%")
            del self.active_trades[sym]

    async def start(self):
        logger.info("⚔️ OMEGA IGNITION. COMMANDER: QUANTUM GOANNA TECH NO LOGICS.")
        await self.exchange.load_markets()
        while True:
            try:
                tickers = await self.exchange.fetch_tickers()
                targets = [s for s, t in tickers.items() if '/USDT' in s and t['quoteVolume'] > 2000000]
                targets.sort(key=lambda x: tickers[x]['percentage']) # Hunt the dips

                # Manage active fleet
                for sym in list(self.active_trades.keys()): 
                    await self.check_exit(sym)

                # Deploy new slots
                if len(self.active_trades) < self.max_slots:
                    current_slot_idx = len(self.active_trades)
                    for pair in targets[:40]:
                        if pair in self.active_trades: continue
                        ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='5m', limit=50)
                        df = pd.DataFrame(ohlcv, columns=['t','o','h','l','c','v'])
                        
                        signal = await self.apply_strategy(pair, df, current_slot_idx)
                        mlofi = await self.get_mlofi(pair)

                        # BERSERKER slots (12+) ignore MLOFI for maximum aggression
                        mlofi_passed = mlofi > self.mlofi_shield if current_slot_idx < 12 else True

                        if signal and mlofi_passed:
                            order = await self.exchange.create_market_buy_order(pair, self.stake)
                            self.active_trades[pair] = {
                                'entry': order['price'] or ticker['last'], 
                                'qty': order['filled'], 
                                'wing': signal
                            }
                            logger.info(f"🚀 STRIKE [{signal}]: {pair} - Slot {current_slot_idx}")
                            break
            except Exception as e: 
                logger.error(f"💀 PERIMETER BREECH: {e}")
            await asyncio.sleep(10)
