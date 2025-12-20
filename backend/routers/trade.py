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
    try:
        result = await oms.place_order(order.symbol, order.side, order.amount, order.type)
        return {"status": "success", "order": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
