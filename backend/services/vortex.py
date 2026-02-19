import asyncio, os, logging, ccxt.async_support as ccxt
import pandas as pd
import pandas_ta as ta

# T.I.A. OPERATOR LOG
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [OPERATOR] - %(message)s')
logger = logging.getLogger("vortex")

class VortexBerserker:
    def __init__(self):
        self.base_stake = 10.50
        self.min_notional = 5.05
        self.universe = ["SOL/USDT", "XRP/USDT", "DOGE/USDT", "PEPE/USDT", "ADA/USDT"]
        self.exchange = ccxt.mexc({
            'apiKey': os.getenv('MEXC_API_KEY'), 
            'secret': os.getenv('MEXC_SECRET'), 
            'options': {'createMarketBuyOrderRequiresPrice': False}
        })

    async def start(self):
        logger.info("⚔️ CITADEL V8.9: BERSERKER LIVE. CLEARING DECKS.")
        await self.exchange.load_markets()
        
        # --- COMMAND 1: Nuke XLM to fund the tank ---
        try:
            bal = await self.exchange.fetch_balance()
            xlm_qty = bal['free'].get('XLM', 0)
            if xlm_qty > 10: # If we have more than $2 worth
                await self.exchange.create_market_sell_order("XLM/USDT", xlm_qty)
                logger.info(f"💰 DECK CLEARED: Sold {xlm_qty} XLM. Strike pool funded.")
        except Exception as e: logger.error(f"XLM Dump Failed: {e}")

        while True:
            for pair in self.universe:
                try:
                    # Check MLOFI (The Shield)
                    ob = await self.exchange.fetch_order_book(pair, limit=5)
                    bids = sum([v for p, v in ob['bids']])
                    asks = sum([v for p, v in ob['asks']])
                    if (bids - asks) / (bids + asks) < 0.08: continue

                    # Check P25 (The Sniper)
                    ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='5m', limit=50)
                    df = pd.DataFrame(ohlcv, columns=['t','o','h','l','c','v'])
                    rsi = ta.rsi(df['c']).iloc[-1]
                    if rsi < 30:
                        await self.exchange.create_market_buy_order(pair, self.base_stake)
                        logger.info(f"✅ SNIPER STRIKE: Bought {pair} at RSI {rsi:.2f}")
                except: continue
            await asyncio.sleep(60)

VortexEngine = VortexBerserker
