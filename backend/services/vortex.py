import os
import ccxt.async_support as ccxt
import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger("[T.I.A.]")

class VortexBerserker:
    def __init__(self):
        # 1. ATOMIC INITIALIZATION (Kills the AttributeError)
        self.exchange = None
        self.is_alive = True
        self.start_time = asyncio.get_event_loop().time()
        self.active_positions = {}
        
        # 2. LOAD CREDENTIALS
        self.api_key = os.getenv('MEXC_API_KEY')
        self.secret = os.getenv('MEXC_SECRET')

        # 3. INITIALIZE EXCHANGE
        if self.api_key and self.secret:
            try:
                self.exchange = ccxt.mexc({
                    'apiKey': self.api_key,
                    'secret': self.secret,
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'}
                })
                logger.info("✅ MEXC Connection Established.")
            except Exception as e:
                logger.error(f"🚨 Exchange Init Failed: {e}")
        else:
            logger.error("🚨 Missing MEXC Environment Variables.")

    def get_status(self) -> Dict[str, Any]:
        """Returns diagnostic data for the API and Dashboard."""
        return {
            "status": "RUNNING" if self.is_alive else "STOPPED",
            "exchange_connected": self.exchange is not None,
            "uptime": f"{int(asyncio.get_event_loop().time() - self.start_time)}s",
            "active_trades": len(self.active_positions),
            "version": "V3.1.1-Hardened"
        }

    async def stop_engine(self):
        """The Omega-Stop Logic"""
        self.is_alive = False
        logger.warning("🚨 KILL-SWITCH TRIGGERED. Shutting down...")
        if self.exchange:
            await self.exchange.close()

    async def start(self):
        """The Main Trading Loop"""
        if not self.exchange:
            logger.error("❌ Cannot start engine: Exchange is None.")
            return

        logger.info("🚀 VortexBerserker loop ignited.")
        while self.is_alive:
            try:
                # --- INSERT STRATEGY LOGIC HERE ---
                # Example: await self.check_rsi_signals()
                await asyncio.sleep(60) 
            except Exception as e:
                logger.error(f"⚠️ Loop Error: {e}")
                await asyncio.sleep(30)