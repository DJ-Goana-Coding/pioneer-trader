import os
import uvicorn
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

# --- THE VORTEX ENGINE HEARTBEAT ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This is where your 7-slot loop lives
    print("🛰️ T.I.A. COMMAND: VORTEX HEARTBEAT ACTIVE.")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def health_check():
    return {"status": "🟢 LIVE", "region": "Frankfurt", "engine": "Vortex v2"}

if __name__ == "__main__":
    # CRITICAL: This line fixes the Render Timeout error
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 IGNITION: Binding to Port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)