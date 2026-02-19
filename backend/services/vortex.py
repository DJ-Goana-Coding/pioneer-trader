import asyncio, os, logging, ccxt.async_support as ccxt
import pandas as pd
import pandas_ta as ta

# T.I.A. OPERATOR HUD
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [OPERATOR] - %(message)s')
logger = logging.getLogger("vortex")

class VortexBerserker:
    def __init__(self):
        self.base_stake = 11.25  # Pulley Arc Scaling ($15 * 0.75)
        self.universe = [] # Fetched dynamically
        self.exchange = ccxt.mexc({
            'apiKey': os.getenv('MEXC_API_KEY'), 
            'secret': os.getenv('MEXC_SECRET'), 
            'options': {'createMarketBuyOrderRequiresPrice': False}
        })

    async def start(self):
        logger.info("⚔️ CITADEL V8.9: 16-SLOT BERSERKER LIVE. EXTRACTION INITIATED.")
        await self.exchange.load_markets()
        
        while True:
            # Oracle Check: Scan high volume USDT pairs
            markets = await self.exchange.fetch_tickers()
            targets = [s for s, t in markets.items() if '/USDT' in s and t['quoteVolume'] > 500000]

            for pair in targets[:16]: # Iterate through 16 potential slots
                try:
                    # MLOFI Shield (8% Imbalance)
                    ob = await self.exchange.fetch_order_book(pair, limit=5)
                    bids = sum([v for p, v in ob['bids']])
                    asks = sum([v for p, v in ob['asks']])
                    if (bids - asks) / (bids + asks) < 0.08: continue

                    # P25 Sniper Entry
                    ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='5m', limit=50)
                    df = pd.DataFrame(ohlcv, columns=['t','o','h','l','c','v'])
                    rsi = ta.rsi(df['c']).iloc[-1]
                    
                    if rsi < 30:
                        await self.exchange.create_market_buy_order(pair, self.base_stake)
                        logger.info(f"✅ STRIKE: Bought {pair} at RSI {rsi:.2f}")
                except: continue
            await asyncio.sleep(60)

VortexEngine = VortexBerserker
