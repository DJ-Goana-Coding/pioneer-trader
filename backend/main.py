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
        from backend.services.vortex import VortexEngine
        vortex = VortexEngine()
        
        # Engage Background Loop
        asyncio.create_task(vortex.start_loop())
        logger.info("🏰 CITADEL: Vortex Engine Engaged")
    except Exception as e:
        logger.error(f"🚨 IGNITION FAILURE: {e}")

@app.get("/")
async def root():
    return {"status": "Citadel Online", "engine": "Vortex V5.3"}

@app.get("/telemetry")
async def get_telemetry():
    if not vortex: return {"status": "Starting..."}
    return {
        "status": "Active",
        "wallet": f"${vortex.wallet_balance:.2f}",
        "equity": f"${vortex.total_equity:.2f}",
        "slots": vortex.slot_status
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=10000)
    
