from fastapi import FastAPI, APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel

from backend.routers import auth
from backend.core.security import get_current_admin
from backend.services.strategy_engine import StrategyEngine
from backend.services.proxy_service import ProxyService

app = FastAPI()

# --- Services ---
strategy_engine = StrategyEngine()
proxy_service = ProxyService()

# --- Auth Router ---
app.include_router(auth.router)

# --- Models ---
class ReloadReq(BaseModel):
    strategy: str

# --- Public Endpoints ---
@app.get("/")
async def root():
    return {"status": "ok", "message": "Frankfurt Citadel online (Protected)"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/healthz")
async def healthz():
    return {"status": "healthy", "uptime": "ok"}

# --- PROTECTED Endpoints (Require Admin Token) ---
@app.get("/telemetry")
async def telemetry(admin: str = Depends(get_current_admin)):
    return await strategy_engine.get_telemetry()

@app.post("/strategy/reload")
async def reload(r: ReloadReq, admin: str = Depends(get_current_admin)):
    await strategy_engine.reload_strategy(r.strategy)
    return {"status": "reloaded"}

# --- Proxy Stub ---
proxy = APIRouter()
@proxy.api_route("/proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_stub(path: str, request: Request):
    return {"proxy": "active", "path": path}

app.include_router(proxy)
