import uvicorn
import sys
import os
from fastapi import FastAPI, BackgroundTasks

# THE SERVICE BRIDGE: Force Python to see the 'services' sub-folder
current_dir = os.path.dirname(os.path.abspath(__file__))
services_path = os.path.join(current_dir, 'services')
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

# --- Financial Scout sidecar ---------------------------------------------
# Scaffolding only: links ISO 20022 parser + Yield Engine behind the
# existing JWT guard. Finance logic will be verified in a later sweep.
try:
    from backend.routers.finance import router as finance_router
    app.include_router(finance_router)
except Exception as _finance_exc:  # pragma: no cover - import guard
    print(f"WARN: finance router not loaded: {_finance_exc}")

# --- Hub synapse ----------------------------------------------------------
# Welds this node to the central 'mapping-and-inventory' Hub by exposing
# /v1/ingest and /v1/query that forward to the global FAISS vector store.
try:
    from backend.routers.hub_router import router as hub_router
    app.include_router(hub_router)
except Exception as _hub_exc:  # pragma: no cover - import guard
    print(f"WARN: hub router not loaded: {_hub_exc}")

@app.get("/health")
async def health():
    balance = await vortex.get_balance()
    return {"status": "ONLINE", "usdt": balance['total'].get('USDT', 0)}

@app.get("/strike/{side}/{symbol}/{amount}")
async def manual_strike(side: str, symbol: str, amount: float):
    return await vortex.execute_trade(symbol, side, amount)

@app.get("/start/{symbol}")
async def start_vortex(symbol: str, tasks: BackgroundTasks):
    tasks.add_task(vortex.monitor_market, symbol)
    return {"message": f"Vortex monitoring {symbol} initiated."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
