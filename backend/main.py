from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
import asyncio
import os
import logging
from backend.services.vortex import VortexBerserker

# THE ARCHITECT'S TACTICAL LOGGER
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [T.I.A.] - %(message)s')
logger = logging.getLogger("citadel")

app = FastAPI(title="Frankfurt Citadel")
vortex = VortexBerserker()

# 🛡️ GLOBAL FRACTURE REPAIR: Catch 500 Errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"💀 DISTRICT 01 FRACTURE: {exc}")
    return JSONResponse(
        status_code=500,
        content={"status": "ERROR", "msg": f"Fracture: {str(exc)}", "action": "Check Render Environment Variables"}
    )

@app.on_event("startup")
async def startup_event():
    """Ignition sequence for the 16-slot fleet"""
    logger.info("⚔️ CITADEL IGNITION: Pushing all 16 slots live.")
    # Ensure background tasks have their own error handling to avoid the 500 loop
    asyncio.create_task(vortex.start())

@app.get("/")
async def root():
    return {
        "status": "Citadel Online",
        "engine": "Vortex V8.9 Berserker",
        "commander": "Darrell",
        "message": "Visit /health for live telemetry."
    }

@app.get("/health")
async def health():
    """Live Telemetry for your Mobile Command"""
    try:
        active_slots = len([s for s in vortex.slots.values() if s.get('active', False)])
        return {
            "status": "ok",
            "universe": "MEXC_GLOBAL_USDT",
            "active_slots": f"{active_slots}/16",
            "mlofi_gate": vortex.mlofi_gate,
            "exchange_connected": vortex.exchange is not None,
            "fuel_tank": "Consolidated (XLM Dumped)"
        }
    except Exception as e:
        logger.error(f"Health Check Fracture: {e}")
        return {"status": "degraded", "error": str(e)}

@app.post("/omega-stop")
async def omega_stop(auth_token: str = Header(None)):
    """The Mobile Kill-Switch"""
    if auth_token != os.getenv("KILL_AUTH_TOKEN"):
        logger.warning("🚫 UNAUTHORIZED KILL SIGNAL DETECTED.")
        raise HTTPException(status_code=403, detail="Unauthorized Kill Signal")
    
    logger.info("🛑 SYSTEM_NUKLEUS_HALT: Shutting down Citadel nodes.")
    os._exit(0) # Hard exit for the monolith
