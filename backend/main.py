from backend.services.proxy_service import ProxyService
from fastapi import FastAPI, APIRouter, Request, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
, APIRouter, Request
from backend.core.config import settings
from backend.routers import auth, telemetry, strategy, trade, brain
from backend.services.exchange import ExchangeService
from backend.services.oms import OMS
from backend.services.strategy_engine import StrategyEngine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting Pioneer-Admiral V1 in {settings.EXECUTION_MODE} mode...")
    
    # Initialize Services
    exchange_service = ExchangeService()
    await exchange_service.initialize()
    
    strategy_engine = StrategyEngine()
    oms = OMS(exchange_service)
    
    # Dependency Injection
    app.state.exchange_service = exchange_service
    app.state.strategy_engine = strategy_engine
    app.state.oms = oms
    
    yield
    
    # Shutdown
    print("Shutting down Pioneer-Admiral V1...")
    await exchange_service.shutdown()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Include Routers
app.include_router(auth.router)
app.include_router(telemetry.router)
app.include_router(strategy.router)
app.include_router(trade.router)
app.include_router(brain.router)

@app.get("/")
async def root():
    return {"message": "Pioneer-Admiral V1 Online", "mode": settings.EXECUTION_MODE}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)


@app.get("/healthz")
async def healthz():
    return {"status": "healthy", "uptime": "ok"}


proxy = APIRouter()
@proxy.api_route("/proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_stub(path: str, request: Request):
    return {"status": "proxy_stub"}
app.include_router(proxy)

class ReloadReq(BaseModel): strategy: str
@app.post("/strategy/reload")
async def reload(r: ReloadReq):
    await strategy_engine.reload_strategy(r.strategy)
    return {"status": "reloaded"}

@app.get("/telemetry")
async def telemetry():
    return await strategy_engine.get_telemetry()
