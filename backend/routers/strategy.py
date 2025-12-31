from fastapi import APIRouter, Depends, Request
from backend.core.security import get_current_user
from backend.services.strategy_engine import StrategyEngine
from backend.services.exchange import ExchangeService

router = APIRouter(prefix="/strategy", tags=["strategy"])

@router.get("/analyze/{symbol:path}", dependencies=[Depends(get_current_user)])
async def analyze_symbol(symbol: str, request: Request):
    exchange_service: ExchangeService = request.app.state.exchange_service
    strategy_engine: StrategyEngine = request.app.state.strategy_engine
    
    # Fetch data
    df = await exchange_service.fetch_ohlcv(symbol)
    
    # Run strategy
    df = strategy_engine.calculate_indicators(df)
    signal = strategy_engine.check_signal(df)
    
    # Return last few rows and signal
    return {
        "symbol": symbol,
        "signal": signal,
        "data": df.tail(5).to_dict(orient="records")
    }

@router.get("/swarm-analyze/{symbol:path}", dependencies=[Depends(get_current_user)])
async def swarm_analyze_symbol(symbol: str, request: Request):
    """Analyze symbol using the Phi-3.5 drone swarm"""
    exchange_service: ExchangeService = request.app.state.exchange_service
    strategy_engine: StrategyEngine = request.app.state.strategy_engine
    swarm = request.app.state.swarm
    
    # Fetch data
    df = await exchange_service.fetch_ohlcv(symbol)
    df = strategy_engine.calculate_indicators(df)
    
    # Get consensus from swarm
    data_dict = df.tail(5).to_dict(orient="records")
    consensus = await swarm.consensus_analysis(symbol, {"data": data_dict})
    
    # Also get traditional signal
    traditional_signal = strategy_engine.check_signal(df)
    
    return {
        "symbol": symbol,
        "traditional_signal": traditional_signal,
        "swarm_consensus": consensus,
        "data": data_dict
    }
