import os
import asyncio
import uvicorn
from fastapi import FastAPI
from vortex import VortexOmega

app = FastAPI(title="Frankfurt Citadel")
vortex = VortexOmega()

@app.on_event("startup")
async def startup_event():
    # District 01 Ignition: Fires the 16-slot array
    asyncio.create_task(vortex.start())

@app.get("/")
async def root():
    return {"status": "ONLINE", "commander": "Darrell", "engine": "Vortex V10"}

@app.get("/health")
async def health():
    return {"status": "ok", "active_slots": f"{len(vortex.active_trades)}/16"}

if __name__ == "__main__":
    # CRITICAL: Render will kill the app if it doesn't find this Port
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
