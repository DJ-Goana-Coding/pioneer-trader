import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.services.vortex import VortexEngine
from backend.core.logging_config import setup_logging

# T.I.A. Cockpit imports
from backend.services.tia_agent import tia_agent
from backend.services.admiral_engine import admiral_engine
from backend.services.tia_admiral_bridge import tia_admiral_bridge
from backend.services.garage_manager import garage_manager
from backend.routers.cockpit import router as cockpit_router

# V19 Security & Archival imports
from backend.routers.security import router as security_router

logger = setup_logging("backend.main")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
bot = VortexEngine()

# Register T.I.A. Cockpit components
app.state.tia_agent = tia_agent
app.state.admiral_engine = admiral_engine
app.state.tia_admiral_bridge = tia_admiral_bridge
app.state.garage_manager = garage_manager
app.state.vortex = bot

# Include routers
app.include_router(cockpit_router)
app.include_router(security_router)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting Pioneer Trader backend...")
    logger.info("🦎 T.I.A. Cockpit: ACTIVE")
    logger.info("⚔️ Admiral Engine: ACTIVE")
    logger.info("🌉 T.I.A.-Admiral Bridge: ACTIVE")
    logger.info("🏁 Genesis Garage Manager: ACTIVE")
    logger.info("🛡️ V19 Security Scanner: ARMED")
    logger.info("📦 V19 Shadow Archive: ACTIVE")
    asyncio.create_task(bot.start_loop())

# FIX: Allow HEAD requests so Render health checks stay green
@app.head("/")
@app.get("/")
async def home():
    try:
        return {
            "status": "LIVE",
            "wallet_balance": f"{bot.wallet_balance:.2f}",
            "total_equity": f"{bot.total_equity:.2f}",
            "total_profit": f"{bot.total_profit:.2f}",
            "active_slots": bot.active_slots,
            "next_slot_cost": f"{bot.next_slot_price:.2f}",
            "held_coins": bot.held_coins,
            "slot_status": bot.slot_status
        }
    except Exception as e:
        logger.error(f"Error in home endpoint: {e}")
        return {"status": "ERROR", "message": str(e)}