from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import asyncio, os
from backend.services.vortex import VortexEngine

app = FastAPI(title="Frankfurt Citadel")
vortex = VortexEngine()

@app.get("/")
@app.head("/")
async def root():
    return {"status": "Citadel Online", "engine": "Vortex V10.0 Omega"}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(vortex.start())

@app.get("/health")
async def health():
    return {"status": "ok", "slots": f"{len(vortex.active_trades)}/16", "balance_mode": "AGGRESSIVE"}
