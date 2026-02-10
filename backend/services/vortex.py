import asyncio
import pandas as pd
import pandas_ta as ta
import ccxt.async_support as ccxt
import os
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [T.I.A.] - %(message)s')

class VortexBerserker:
    def __init__(self):
        self.base_stake, self.ladder_step = 10.50, 5.00
        self.state_file = "vortex_state.json"
        self.slots = self._load_state()
        self.exchange = ccxt.mexc({'apiKey': os.getenv('MEXC_API_KEY'), 'secret': os.getenv('MEXC_SECRET'), 'enableRateLimit': True, 'options': {'defaultType': 'spot'}})

    def _load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f: return json.load(f)
            except: pass
        return {f"Slot_{i}": {"wing": w, "active": False, "rung": 0, "pair": None, "entry": 0.0, "qty": 0.0} 
                for i, w in enumerate(["PIRANHA", "HARVESTER", "HARVESTER", "SNIPER", "BANKER", "BEAR", "CRAB"], 1)}

    def _save_state(self):
        with open(self.state_file, 'w') as f: json.dump(self.slots, f, indent=4)

    async def get_active_markets(self):
        try:
            m = await self.exchange.load_markets()
            return [p for p in m if p.endswith('/USDT') and m[p]['active']]
        except: return ["SOL/USDT", "XRP/USDT"]

    async def get_mlofi(self, pair):
        try:
            ob = await self.exchange.fetch_order_book(pair, limit=10)
            bids, asks = sum([v for p, v in ob['bids'][:5]]), sum([v for p, v in ob['asks'][:5]])
            return (bids - asks) / (bids + asks) > 0.08
        except: return False

    async def check_strategy(self, pair, wing):
        try:
            ohlcv = await self.exchange.fetch_ohlcv(pair, timeframe='5m', limit=50)
            df = pd.DataFrame(ohlcv, columns=['t','o','h','l','c','v'])
            rsi, ema, price = ta.rsi(df['c']).iloc[-1], ta.ema(df['c'], 50).iloc[-1], df['c'].iloc[-1]
            if wing == "PIRANHA": return rsi < 25
            if wing == "HARVESTER": return rsi < 30 and price > ema
            if wing == "SNIPER": return rsi < 18
            if wing == "BANKER": return rsi < 14
            if wing == "BEAR": return price < ema and rsi < 25
            if wing == "CRAB": return 48 < rsi < 52
            return False
        except: return False

    async def execute_trade(self, slot_id, side, pair=None, stake_usdt=0):
        slot = self.slots[slot_id]
        try:
            if side == 'buy':
                ticker = await self.exchange.fetch_ticker(pair)
                price = ticker['last']
                qty = stake_usdt / price
                order = await self.exchange.create_market_buy_order(pair, qty)
                logging.info(f"✅ LIVE BUY: {pair} @ ${price}")
                slot.update({"active": True, "pair": pair, "entry": price, "qty": qty})
            else:
                await self.exchange.create_market_sell_order(slot['pair'], slot['qty'])
                logging.info(f"💰 LIVE SELL: {slot['pair']}")
                slot.update({"active": False, "pair": None, "rung": (slot['rung'] + 1) % 10})
            self._save_state()
        except Exception as e: logging.error(f"❌ CRITICAL: {e}")

    async def check_exit(self, slot_id):
        slot = self.slots[slot_id]
        try:
            ticker = await self.exchange.fetch_ticker(slot['pair'])
            pct = (ticker['last'] - slot['entry']) / slot['entry']
            tp, sl = 0.015, -0.012
            if slot['wing'] == "SNIPER": tp = 0.05
            if pct >= tp or pct <= sl: await self.execute_trade(slot_id, 'sell')
        except: pass

    async def run_slot(self, s_id):
        while True:
            slot = self.slots[s_id]
            if not slot['active']:
                universe = await self.get_active_markets()
                for pair in universe:
                    if await self.get_mlofi(pair) and await self.check_strategy(pair, slot['wing']):
                        stake = self.base_stake + (slot['rung'] * self.ladder_step)
                        await self.execute_trade(s_id, 'buy', pair, stake)
                        break
                    await asyncio.sleep(0.5)
            else: await self.check_exit(s_id)
            await asyncio.sleep(30)

    async def start(self):
        logging.info("🏰 CITADEL LIVE FIRE: GLOBAL UNIVERSE ENGAGED")
        tasks = [self.run_slot(s_id) for s_id in self.slots]
        await asyncio.gather(*tasks)

VortexEngine = VortexBerserker