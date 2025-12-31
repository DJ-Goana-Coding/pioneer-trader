from fastapi import APIRouter, Depends, Request, HTTPException
from backend.core.security import get_current_user
from backend.services.oms import OMS
from pydantic import BaseModel

router = APIRouter(prefix="/trade", tags=["trade"])

class OrderRequest(BaseModel):
    symbol: str
    side: str
    amount: float
    type: str = "market"

@router.post("/order", dependencies=[Depends(get_current_user)])
async def place_order(order: OrderRequest, request: Request):
    oms: OMS = request.app.state.oms
    scanner = request.app.state.scanner
    archival = request.app.state.archival
    
    # Security scan on order data
    scan_result = scanner.scan_request_data(order.dict(), "trade_order")
    if scan_result["status"] == "threat_detected":
        raise HTTPException(
            status_code=400, 
            detail=f"Security threat detected: {scan_result['threats']}"
        )
    
    try:
        result = await oms.place_order(order.symbol, order.side, order.amount, order.type)
        
        # Log trade to archival
        trade_log = {
            "symbol": order.symbol,
            "side": order.side,
            "amount": order.amount,
            "type": order.type,
            "status": "WIN" if result.get("status") == "closed" else "PENDING",
            "order_id": result.get("id"),
            "price": result.get("price")
        }
        archival.log_trade(trade_log)
        
        return {"status": "success", "order": result}
    except ValueError as e:
        # Log failed trade
        archival.log_trade({
            "symbol": order.symbol,
            "side": order.side,
            "amount": order.amount,
            "type": order.type,
            "status": "LOSS",
            "error": str(e)
        })
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
