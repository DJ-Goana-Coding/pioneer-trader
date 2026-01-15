import asyncio
import ccxt.async_support as ccxt
import os
import pandas as pd
from backend.services.strategies import StrategyLogic

class Slot:
    def __init__(self, id):
        self.id = id
        self.capital = 10.50
        self.status = "IDLE"  # IDLE, HUNTING, ACTIVE
        self.asset = "None"
        self.pnl = 0.0

class VortexEngine:
    def __init__(self):
        # 7-Slot Worker Array
        self.slots = [Slot(i+1) for i in range(7)]
        self.logic = StrategyLogic()
        self.running = False
        self.exchange = None
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.secret = os.getenv("BINANCE_SECRET_KEY")

    async def _init_exchange(self):
        if not self.exchange and self.api_key:
            self.exchange = ccxt.binance({
                'apiKey': self.api_key, 'secret': self.secret, 
                'enableRateLimit': True, 'options': {'defaultType': 'spot'}
            })

    async def heartbeat(self):
        if not self.running: return
        await self._init_exchange()
        
        # THE HAMMER: Scan Logic
        print(f"💓 Vortex Scanning {len(self.slots)} Slots...")
        # (This is where the bot 'Sees' the market)
        for slot in self.slots:
            if slot.status == "IDLE":
                slot.status = "HUNTING"
                slot.asset = "SCANNING..."

    async def start(self): self.running = True; print("🚀 Vortex STARTED")
    async def stop(self): self.running = False; print("🛑 Vortex STOPPED")
    async def get_telemetry(self):
        return {"status": "RUNNING" if self.running else "STOPPED", 
                "slots": [{"id": s.id, "status": s.status, "asset": s.asset} for s in self.slots]}