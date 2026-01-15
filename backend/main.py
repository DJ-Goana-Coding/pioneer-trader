from fastapi import FastAPI, APIRouter, Request, HTTPException
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pydantic import BaseModel

from backend.services.vortex import VortexEngine
from backend.services.proxy_service import ProxyService

# --- LIFECYCLE ---
scheduler = AsyncIOScheduler()
vortex = VortexEngine()
proxy_service = ProxyService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await vortex.start()
    scheduler.add_job(vortex.heartbeat, 'interval', seconds=10)
    scheduler.start()
    yield
    # Shutdown
    await vortex.stop()

app = FastAPI(lifespan=lifespan)

# --- MODELS ---
class ReloadReq(BaseModel):
    strategy: str

# --- OPEN ENDPOINTS (No Auth) ---
@app.get("/")
async def root():
    return {"status": "ok", "message": "Frankfurt Citadel (Vortex Active - OPEN)"}

@app.get("/healthz")
async def healthz():
    return {"status": "healthy"}

@app.get("/telemetry")
async def telemetry():
    # DIRECT ACCESS to Vortex Telemetry
    return await vortex.get_telemetry()

@app.post("/strategy/reload")
async def reload(r: ReloadReq):
    # DIRECT ACCESS to Reload
    return {"status": "reloaded (mock)", "strategy": r.strategy}

# --- PROXY STUB ---
proxy = APIRouter()
@proxy.api_route("/proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_stub(path: str, request: Request):
    return {"proxy": "active", "path": path}
app.include_router(proxy)
