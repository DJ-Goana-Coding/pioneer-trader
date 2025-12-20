from contextlib import asynccontextmanager
from fastapi import FastAPI
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
