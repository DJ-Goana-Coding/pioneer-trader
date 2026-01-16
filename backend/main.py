import os
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.services.vortex import VortexEngine

app = FastAPI()

# 🛡️ CORS PERMISSION: ALLOW VERCEL TO CONNECT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (Vercel, Localhost, Mobile)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vortex = VortexEngine(active_slots=2)

@app.on_event("startup")
async def startup_event():
    # Start the Heartbeat (Stealth Mode is inside Vortex class)
    asyncio.create_task(vortex.start_loop())
    print("🛰️ T.I.A. COMMAND: VORTEX HEARTBEAT ACTIVE [CORS ENABLED]")

@app.get("/")
def home():
    return {
        "status": "🟢 LIVE",
        "commander": "Darrell",
        "engine": "Vortex v2.1 (Stealth)",
        "active_slots": 2,
        "stake": "10.50 USDT"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)