
from fastapi import FastAPI
from backend.services.vortex import vortex
import uvicorn
import threading

app = FastAPI(title="Frankfurt Citadel API", version="0.9.0")

@app.get("/")
def home():
    return {
        "system": "Frankfurt Citadel",
        "status": "ONLINE",
        "engine_active": vortex.active,
        "cycles": vortex.cycle_count
    }

@app.post("/engine/start")
def start_engine():
    return {"msg": vortex.ignite()}

@app.post("/engine/stop")
def stop_engine():
    return {"msg": vortex.shutdown()}

@app.get("/engine/status")
def engine_status():
    return {
        "active": vortex.active, 
        "loaded_strategies": list(vortex.strategies.keys()),
        "cycles_completed": vortex.cycle_count
    }

# --- THREADED LAUNCHER FOR COLAB ---
def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
