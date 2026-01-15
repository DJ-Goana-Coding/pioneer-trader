
import time
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from backend.engine.binder import RuntimeBinder

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VORTEX")

class VortexEngine:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.binder = RuntimeBinder()
        self.strategies = {}
        self.active = False
        self.cycle_count = 0
        self.wallet = 1000.00  # Paper Money

    def ignite(self):
        """Starts the Engine Loop."""
        if self.active:
            return "⚠️ Vortex is already spinning."
        
        logger.info("🔥 IGNITING VORTEX ENGINE...")
        self.strategies = self.binder.bind_and_load()
        
        # Add the 'Heartbeat' Job (The 60s Tick)
        self.scheduler.add_job(self.tick, 'interval', seconds=5, id='heartbeat')
        self.scheduler.start()
        self.active = True
        return "✅ Vortex Ignition Successful. Systems Green."

    def shutdown(self):
        """Kills the Loop."""
        if not self.active:
            return "⚠️ Vortex is already cold."
        
        self.scheduler.shutdown(wait=False)
        self.active = False
        return "🛑 Vortex Shutdown Complete."

    def tick(self):
        """The Main Loop: Runs every 5 seconds (fast for testing)."""
        self.cycle_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 1. Fetch Data (Mock)
        market_data = {"price": 65000 + (self.cycle_count * 10), "time": timestamp}
        
        # 2. Feed Strategies
        logger.info(f"⏳ CYCLE {self.cycle_count} | Market: {market_data}")
        for s_id, strat in self.strategies.items():
            try:
                strat.run(market_data)
            except Exception as e:
                logger.error(f"❌ Strategy {s_id} Failed: {e}")

# Singleton Instance
vortex = VortexEngine()
