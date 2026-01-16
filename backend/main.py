import os
import asyncio
import uvicorn
from fastapi import FastAPI
from backend.services.vortex import VortexEngine

app = FastAPI()
vortex = VortexEngine(active_slots=2)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(vortex.start_loop())
    print("🛰️ T.I.A. COMMAND: VORTEX HEARTBEAT ACTIVE [2 SLOTS]")

@app.get("/")
def home():
    return {"status": "🟢 LIVE", "commander": "Darrell", "engine": "Vortex v2.1"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)