from fastapi import APIRouter, Depends, HTTPException, Request
from backend.core.security import get_current_user
from backend.services.strategies import StrategyLogic
from backend.services.exchange import ExchangeService

router = APIRouter(prefix="/strategy", tags=["strategy"])

# Map of strategy-name → method name on StrategyLogic.
_STRATEGIES = {
    "p25_momentum": "p25_momentum",
    "golden_cross": "golden_cross",
}


@router.get("/analyze/{symbol:path}", dependencies=[Depends(get_current_user)])
async def analyze_symbol(symbol: str, request: Request, strategy: str = "p25_momentum"):
    if strategy not in _STRATEGIES:
        raise HTTPException(
            status_code=422,
            detail=f"unknown strategy '{strategy}'; choose one of {list(_STRATEGIES)}",
        )

    exchange_service: ExchangeService = getattr(request.app.state, "exchange_service", None)
    strategy_logic: StrategyLogic = getattr(request.app.state, "strategy_logic", None)
    if exchange_service is None or strategy_logic is None:
        raise HTTPException(status_code=503, detail="strategy services not initialised")

    # Fetch candles from the exchange (PAPER mode is safe for analysis)
    df = await exchange_service.fetch_ohlcv(symbol)

    # Run the requested strategy method
    method = getattr(strategy_logic, _STRATEGIES[strategy])
    signal = method(df)

    return {
        "symbol": symbol,
        "strategy": strategy,
        "signal": signal,
        "candles_evaluated": int(len(df)),
        "data": df.tail(5).to_dict(orient="records"),
    }

