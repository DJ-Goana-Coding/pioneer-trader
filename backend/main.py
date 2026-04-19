import json
import os
import re
import sys
from contextlib import asynccontextmanager
from typing import Literal, NoReturn

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError

from backend.core.config import settings
from backend.core.security import get_current_admin
from backend.services.agent_audit import agent_audit

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


# --- Lifespan: initialise app.state services so trade/strategy routers work
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise async services into ``app.state`` on startup.

    The ``trade`` and ``strategy`` routers depend on ``app.state.oms``,
    ``app.state.exchange_service`` and ``app.state.strategy_logic``. We
    instantiate them lazily with import guards so that a missing optional
    dependency (e.g. ``pandas_ta``) cannot crash the whole app.
    """
    app.state.exchange_service = None
    app.state.oms = None
    app.state.strategy_logic = None

    try:
        from backend.services.exchange import ExchangeService
        from backend.services.oms import OMS

        exchange_service = ExchangeService()
        try:
            await exchange_service.initialize()
        except Exception:
            # If init fails mid-way an internal aiohttp session may still be
            # open. Best-effort close to avoid leaks before re-raising into
            # the outer except.
            try:
                await exchange_service.shutdown()
            except Exception:  # pragma: no cover - defensive
                pass
            raise
        app.state.exchange_service = exchange_service
        app.state.oms = OMS(exchange_service)
        agent_audit.record(
            action="exchange_service.initialise",
            payload={"mode": exchange_service.mode},
        )
    except Exception as exc:  # pragma: no cover - startup resilience
        print(f"WARN: ExchangeService/OMS not initialised: {exc}")

    try:
        from backend.services.strategies import StrategyLogic

        app.state.strategy_logic = StrategyLogic()
    except Exception as exc:  # pragma: no cover - optional dep failure
        print(f"WARN: StrategyLogic not initialised: {exc}")

    try:
        yield
    finally:
        if app.state.exchange_service is not None:
            try:
                await app.state.exchange_service.shutdown()
            except Exception as exc:  # pragma: no cover - shutdown resilience
                print(f"WARN: ExchangeService shutdown failed: {exc}")


app = FastAPI(title="CGAL OMEGA TRADER", lifespan=lifespan)
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

# --- Auth router (required for /auth/login tokenUrl) ----------------------
try:
    from backend.routers.auth import router as auth_router
except ImportError as _auth_exc:  # pragma: no cover - import guard
    print(f"WARN: auth router not loaded: {_auth_exc}")
else:
    app.include_router(auth_router)

# --- Telemetry router -----------------------------------------------------
try:
    from backend.routers.telemetry import router as telemetry_router
except ImportError as _telemetry_exc:  # pragma: no cover - import guard
    print(f"WARN: telemetry router not loaded: {_telemetry_exc}")
else:
    app.include_router(telemetry_router)

# --- Cockpit router (T.I.A. + Admiral command center) ---------------------
try:
    from backend.routers.cockpit import router as cockpit_router
except ImportError as _cockpit_exc:  # pragma: no cover - import guard
    print(f"WARN: cockpit router not loaded: {_cockpit_exc}")
else:
    app.include_router(cockpit_router)

# --- Security router (Red Flag Scanner + Shadow Archive) ------------------
try:
    from backend.routers.security import router as security_router
except ImportError as _security_exc:  # pragma: no cover - import guard
    print(f"WARN: security router not loaded: {_security_exc}")
else:
    app.include_router(security_router)

# --- Trade router (depends on app.state.oms from lifespan) ----------------
try:
    from backend.routers.trade import router as trade_router
except ImportError as _trade_exc:  # pragma: no cover - import guard
    print(f"WARN: trade router not loaded: {_trade_exc}")
else:
    app.include_router(trade_router)

# --- Strategy router (depends on app.state.strategy_logic) ----------------
try:
    from backend.routers.strategy import router as strategy_router
except ImportError as _strategy_exc:  # pragma: no cover - import guard
    print(f"WARN: strategy router not loaded: {_strategy_exc}")
else:
    app.include_router(strategy_router)

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


# --- Standardised system status endpoint (PHASE 2.2) ----------------------
# Contract: every node in the QGTNL fleet exposes ``GET /v1/system/status``
# for the Vercel HUD to poll. The shape is intentionally stable so the
# Librarian can index every node uniformly. No auth required — read-only.
@app.get("/v1/system/status", tags=["system"])
async def system_status(request: Request):
    routers_loaded = sorted(
        {
            getattr(r, "tags", [None])[0]
            for r in app.routes
            if getattr(r, "tags", None)
        }
    )
    return {
        "node": "pioneer-trader",
        "status": "ONLINE",
        "version": "v1",
        "execution_mode": settings.EXECUTION_MODE,
        "exchange": "MEXC",
        "routers_loaded": [r for r in routers_loaded if r],
        "services": {
            "exchange_service": getattr(request.app.state, "exchange_service", None) is not None,
            "oms": getattr(request.app.state, "oms", None) is not None,
            "strategy_logic": getattr(request.app.state, "strategy_logic", None) is not None,
        },
        "hub_url": os.environ.get(
            "MAPPING_HUB_URL",
            "https://dj-goana-coding-mapping-and-inventory.hf.space",
        ),
    }


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
    admin: str = Depends(get_current_admin),
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
    # PHASE 2.3: recursive documentation. Audit every authoritative action.
    agent_audit.record(
        action="strike",
        actor=admin,
        payload={"symbol": req.symbol, "side": req.side, "amount": req.amount},
    )
    return await vortex.execute_trade(req.symbol, req.side, req.amount)


@app.post("/start/{symbol}")
async def start_vortex(
    symbol: str,
    tasks: BackgroundTasks,
    admin: str = Depends(get_current_admin),
):
    if not (3 <= len(symbol) <= 20) or not _SYMBOL_RE.match(symbol):
        raise HTTPException(status_code=422, detail="invalid symbol")
    tasks.add_task(vortex.monitor_market, symbol)
    agent_audit.record(action="start_vortex", actor=admin, payload={"symbol": symbol})
    return {"message": f"Vortex monitoring {symbol} initiated."}


if __name__ == "__main__":
    # Match the Dockerfile / HF Space contract: port 10000 by default.
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
