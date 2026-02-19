from fastapi import FastAPI
import asyncio, os
from vortex import VortexOmega

app = FastAPI(title="Frankfurt Citadel")
vortex = VortexOmega()

@app.get("/")
@app.head("/")
async def root():
    return {
        "status": "Citadel Online", 
        "engine": "Vortex V10.0 Omega",
        "commander": "Quantum Goanna Tech No Logics"
    }

@app.on_event("startup")
async def startup_event():
    # Ignite the engine in the background
    asyncio.create_task(vortex.start())

@app.get("/health")
async def health():
    return {
        "status": "ok", 
        "slots": f"{len(vortex.active_trades)}/16", 
        "balance_mode": "AGGRESSIVE",
        "oracle_sync": "active"
    }
