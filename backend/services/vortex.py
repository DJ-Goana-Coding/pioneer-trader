import asyncio
import pandas_ta as ta
import json, os, time, ccxt.async_support as ccxt
from fastapi import FastAPI
import uvicorn, threading
import base64

# [T.I.A.] Liveness Anchor for Hugging Face
app = FastAPI()
@app.get("/")
async def health(): return {"status": "ACTIVE", "commander": "Darrell", "fleet": "10-SLOT-VULTURE"}

class VortexBerserker:
    def __init__(self):
        self.active_positions = {}
        self.universe = ["SOL/USDT", "XRP/USDT", "PEPE/USDT", "SUI/USDT", "ADA/USDT", "MATIC/USDT", "LINK/USDT", "AVAX/USDT", "DOT/USDT", "LTC/USDT"]
        self.base_stake = 10.00 * float(os.getenv("VORTEX_AGGRESSION_MULTIPLIER", 1.0))
        self.stop_loss = 0.012 # 1.2% Hard Shield

    async def calculate_mlofi(self, symbol):
        """[T.I.A.] Multi-Level Order Flow Imbalance"""
        try:
            ob = await self.exchange.fetch_order_book(symbol)
            bid_vol = sum([b[1] for b in ob['bids'][:5]])
            ask_vol = sum([a[1] for a in ob['asks'][:5]])
            return (bid_vol - ask_vol) / (bid_vol + ask_vol)
        except: return 0

    async def check_momentum(self, symbol, df):
        """[T.I.A.] Stagnation momentum check"""
        return df['close'].iloc[-1] > df['close'].shift(6).iloc[-1]

    async def get_signal(self, df, wing_type, symbol):
        mlofi = await self.calculate_mlofi(symbol)
        if mlofi < -0.1 and df['volume'].iloc[-1] > 10000000: return "HOLD" # MLOFI Shield
        
        rsi = ta.rsi(df['close'], length=14).iloc[-1]
        if wing_type == "Piranha" and rsi < 25: return "BUY"
        if wing_type == "Harvester" and rsi < 30 and df['close'].iloc[-1] > ta.ema(df['close'], length=50).iloc[-1]: return "BUY"
        return "HOLD"

    async def execute_websocket_kill(self):
        """[T.I.A.] Panic Protocol: Market Sell All"""
        for symbol, pos in list(self.active_positions.items()):
            await self.exchange.create_market_sell_order(symbol, pos['qty'])
        self.active_positions.clear()
        os._exit(1) # Sever node

# Start Liveness Server
def start_liveness(): uvicorn.run(app, host="0.0.0.0", port=7860)
threading.Thread(target=start_liveness, daemon=True).start()