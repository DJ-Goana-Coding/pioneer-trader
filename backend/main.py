from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.core.config import settings
from backend.routers import auth, telemetry, strategy, trade, brain
from backend.services.exchange import ExchangeService
from backend.services.oms import OMS
from backend.services.strategy_engine import StrategyEngine
from backend.services.swarm import SwarmController
from backend.services.malware_protection import scanner
from backend.services.archival import archival_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting Pioneer-Admiral V1 in {settings.EXECUTION_MODE} mode...")
    print(f"UI Theme: {settings.UI_THEME} | Safety Modulator: {settings.SAFETY_MODULATOR}")
    
    # Initialize Services
    exchange_service = ExchangeService()
    await exchange_service.initialize()
    
    strategy_engine = StrategyEngine()
    oms = OMS(exchange_service)
    
    # Initialize V19 Swarm
    swarm = SwarmController()
    await swarm.initialize()
    
    # Initialize malware protection
    print(f"🛡️ Red Flag Malware Protection: {scanner.get_status()['status']}")
    
    # Initialize archival
    print(f"📦 Shadow Archive: {settings.SHADOW_ARCHIVE_PATH}")
    
    # Dependency Injection
    app.state.exchange_service = exchange_service
    app.state.strategy_engine = strategy_engine
    app.state.oms = oms
    app.state.swarm = swarm
    app.state.scanner = scanner
    app.state.archival = archival_service
    
    yield
    
    # Shutdown
    print("Shutting down Pioneer-Admiral V1...")
    await exchange_service.shutdown()
    await swarm.shutdown()

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
    return {
        "message": "Pioneer-Admiral V1 Online - V19 Fleet Command",
        "mode": settings.EXECUTION_MODE,
        "ui_theme": settings.UI_THEME,
        "safety_modulator": settings.SAFETY_MODULATOR,
        "version": "V19"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
