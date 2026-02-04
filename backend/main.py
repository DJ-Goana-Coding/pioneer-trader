# ================================================================
# 🚀 PIONEER TRADER BACKEND - CITADEL GATEWAY
# ================================================================
from fastapi import FastAPI
import asyncio
import uvicorn
from backend.core.logging_config import setup_logging

logger = setup_logging("main")
app = FastAPI(title="Citadel API")

# GLOBAL ENGINE HOLDER
vortex = None

@app.on_event("startup")
async def startup_event():
    """Starts the Vortex Engine on API Ignition"""
    global vortex
    try:
        # DELAYED IMPORT TO PREVENT CIRCULAR LOOPS
        from backend.services.vortex import VortexBerserker
        vortex = VortexBerserker()
        
        # Engage Background Loop
        asyncio.create_task(vortex.start())
        logger.info("🏰 CITADEL: VortexBerserker Engine Engaged")
    except Exception as e:
        logger.error(f"🚨 IGNITION FAILURE: {e}")

@app.get("/")
async def root():
    return {"status": "Citadel Online", "engine": "Vortex V6.9 Berserker"}

@app.get("/telemetry")
async def get_telemetry():
    if not vortex: return {"status": "Starting..."}
    return {
        "status": "Active",
        "wallet": f"${vortex.wallet_balance:.2f}" if hasattr(vortex, 'wallet_balance') else "N/A",
        "equity": f"${vortex.total_equity:.2f}" if hasattr(vortex, 'total_equity') else "N/A",
        "slots": vortex.slot_status if hasattr(vortex, 'slot_status') else {}
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=10000)