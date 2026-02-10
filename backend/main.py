from fastapi import FastAPI, Header, HTTPException
import asyncio
from backend.services.vortex import VortexBerserker
import os

app = FastAPI(title="Frankfurt Citadel")
vortex = VortexBerserker()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(vortex.start())

@app.get("/")
async def root():
    return {"status": "Citadel Online", "engine": "Vortex V6.9 Global Live"}

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "universe": "MEXC_GLOBAL_USDT",
        "active_slots": len([s for s in vortex.slots.values() if s['active']]),
        "exchange_connected": vortex.exchange is not None
    }

@app.post("/omega-stop")
async def omega_stop(auth_token: str = Header(None)):
    if auth_token != os.getenv("KILL_AUTH_TOKEN"):
        raise HTTPException(status_code=403, detail="Unauthorized Kill Signal")
    os._exit(0)