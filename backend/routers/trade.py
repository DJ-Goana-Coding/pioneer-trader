from fastapi import APIRouter, Depends, Request, HTTPException
from backend.core.security import get_current_user
from backend.services.oms import OMS
from pydantic import BaseModel, Field, field_validator
import math

router = APIRouter(prefix="/trade", tags=["trade"])

class OrderRequest(BaseModel):
    symbol: str = Field(..., pattern=r'^[A-Z0-9]+/USDT$', description="Trading pair symbol (e.g., BTC/USDT)")
    side: str = Field(..., pattern=r'^(buy|sell)$', description="Order side: buy or sell")
    amount: float = Field(..., gt=0, description="Order amount in USDT (must be positive)")
    type: str = Field(default="market", pattern=r'^(market|limit)$', description="Order type")
    
    @field_validator('amount', mode='before')
    @classmethod
    def validate_amount(cls, v):
        try:
            v = float(v)
        except (TypeError, ValueError):
            raise ValueError("Amount must be a valid number")
        if math.isnan(v) or math.isinf(v) or v <= 0:  # Reject NaN, ±Infinity, and non-positive values
            raise ValueError("Amount must be a finite positive number")
        if v > 10000:  # Sanity check - adjust based on your risk limits
            raise ValueError("Amount exceeds maximum allowed order size")
        return v

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
