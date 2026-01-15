from fastapi import FastAPI, APIRouter, Request, HTTPException
from pydantic import BaseModel

from backend.services.strategy_engine import StrategyEngine
from backend.services.proxy_service import ProxyService

app = FastAPI()

# --- Services ---
# Initialize the brain and the gateway
strategy_engine = StrategyEngine()
proxy_service = ProxyService()

# --- Models ---
class ReloadReq(BaseModel):
    strategy: str

# --- Core Endpoints ---
@app.get("/")
async def root():
    return {"status": "ok", "message": "Frankfurt Citadel online"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/healthz")
async def healthz():
    return {"status": "healthy", "uptime": "ok"}

@app.get("/telemetry")
async def telemetry():
    return await strategy_engine.get_telemetry()

@app.post("/strategy/reload")
async def reload(r: ReloadReq):
    success = await strategy_engine.reload_strategy(r.strategy)
    if not success:
        raise HTTPException(status_code=400, detail="Strategy reload failed")
    return {"status": "reloaded", "strategy": r.strategy}

# --- Proxy Stub ---
# This router captures 10000 -> 8000 traffic if needed in future
proxy = APIRouter()

@proxy.api_route("/proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_stub(path: str, request: Request):
    return {
        "proxy": "active",
        "path": path,
        "method": request.method,
        "note": "Proxy stub active"
    }

app.include_router(proxy)
