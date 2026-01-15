
import asyncio
from backend.strategies.simple_rsi import RSIStrategy

class StrategyEngine:
    def __init__(self):
        self.rsi = RSIStrategy()
        self.active = False

    async def start(self):
        print("🚀 STRATEGY ENGINE: Online")
        self.active = True
        asyncio.create_task(self.run_loop())

    async def run_loop(self):
        print("🔄 STRATEGY LOOP: Started")
        while self.active:
            try:
                # Fake data for testing
                signal = self.rsi.check_signal({"close": 100})
                if signal == "BUY":
                    print("✅ STRATEGY SIGNAL: RSI says BUY!")
            except Exception as e:
                print(f"⚠️ STRATEGY ERROR: {e}")
            
            await asyncio.sleep(10) # Run every 10 seconds

    async def reload_strategy(self, name: str):
        print(f"🔄 Reloading {name}...")
        return True

    async def get_telemetry(self):
        return {"status": "active", "engine": "Frankfurt"}
