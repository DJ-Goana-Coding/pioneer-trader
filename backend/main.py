import json
import os
import re
import sys
from typing import Literal, NoReturn

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError

from backend.core.security import get_current_admin

# THE SERVICE BRIDGE: Force Python to see the 'services' sub-folder
current_dir = os.path.dirname(os.path.abspath(__file__))
services_path = os.path.join(current_dir, 'services')
if services_path not in sys.path:
    sys.path.append(services_path)

# Now it can find 'vortex' inside 'backend/services/'
try:
    from vortex import VortexOmega
except ImportError as e:
    # Diagnostic fallback
    print(f"DEBUG: Current Sys Path: {sys.path}")
    raise e

app = FastAPI(title="CGAL OMEGA TRADER")
vortex = VortexOmega()

# --- CORS weld ------------------------------------------------------------
# Whitelist the Vercel HUD ('Pioneer Trader' faceplate) so it can stream
# P/L data. Additional origins may be supplied via the ALLOWED_ORIGINS env
# var as a comma-separated list. The canonical Command Face is always
# included.
_DEFAULT_ORIGIN = "https://citadel-nexus-private.vercel.app"
_extra_origins = [
    o.strip()
    for o in os.environ.get("ALLOWED_ORIGINS", "").split(",")
    if o.strip()
]
_allowed_origins = sorted({_DEFAULT_ORIGIN, *_extra_origins})

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# --- Financial Scout sidecar ---------------------------------------------
# Scaffolding only: links ISO 20022 parser + Yield Engine behind the
# existing JWT guard. Finance logic will be verified in a later sweep.
try:
    from backend.routers.finance import router as finance_router
except ImportError as _finance_exc:  # pragma: no cover - import guard
    print(f"WARN: finance router not loaded: {_finance_exc}")
else:
    app.include_router(finance_router)

# --- Hub synapse ----------------------------------------------------------
# Welds this node to the central 'mapping-and-inventory' Hub by exposing
# /v1/ingest and /v1/query that forward to the global FAISS vector store.
try:
    from backend.routers.hub_router import router as hub_router
except ImportError as _hub_exc:  # pragma: no cover - import guard
    print(f"WARN: hub router not loaded: {_hub_exc}")
else:
    app.include_router(hub_router)


# --- Health & readiness ---------------------------------------------------
# /health is a cheap process-liveness probe (no external calls). /ready is
# the deep probe that touches the exchange so orchestrators can distinguish
# "process up" from "ready to serve trades".
@app.get("/health")
async def health():
    return {"status": "ONLINE"}


@app.get("/ready")
async def ready():
    try:
        balance = await vortex.get_balance()
    except Exception as exc:  # pragma: no cover - exchange failure path
        raise HTTPException(status_code=503, detail=f"exchange unavailable: {exc}")
    usdt = 0
    if isinstance(balance, dict):
        totals = balance.get("total") or {}
        if isinstance(totals, dict):
            usdt = totals.get("USDT", 0)
    return {"status": "READY", "usdt": usdt}


# --- Strike lock ----------------------------------------------------------
# Manual trade execution. POST-only, JWT-guarded, body-validated. The float
# `amount` is bounded and required to be a finite, positive number.
_SYMBOL_PATTERN = r"^[A-Z0-9]+(?:[/\-][A-Z0-9]+)?$"
_SYMBOL_RE = re.compile(_SYMBOL_PATTERN)


class StrikeRequest(BaseModel):
    side: Literal["buy", "sell"]
    symbol: str = Field(min_length=3, max_length=20, pattern=_SYMBOL_PATTERN)
    amount: float = Field(gt=0, le=1_000_000, allow_inf_nan=False)


def _reject_nonfinite(token: str) -> NoReturn:
    raise ValueError(f"non-finite numeric literal not allowed: {token}")


@app.post("/strike")
async def manual_strike(
    request: Request,
    _admin: str = Depends(get_current_admin),
):
    # Pre-parse JSON ourselves so we can reject NaN/Infinity tokens that
    # would otherwise land in the validation error body and break the
    # JSON response renderer.
    raw = await request.body()
    try:
        payload = json.loads(raw or b"{}", parse_constant=_reject_nonfinite)
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=422, detail=f"invalid JSON body: {exc}")
    try:
        req = StrikeRequest.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors(include_url=False))
    return await vortex.execute_trade(req.symbol, req.side, req.amount)


@app.post("/start/{symbol}")
async def start_vortex(
    symbol: str,
    tasks: BackgroundTasks,
    _admin: str = Depends(get_current_admin),
):
    if not (3 <= len(symbol) <= 20) or not _SYMBOL_RE.match(symbol):
        raise HTTPException(status_code=422, detail="invalid symbol")
    tasks.add_task(vortex.monitor_market, symbol)
    return {"message": f"Vortex monitoring {symbol} initiated."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
