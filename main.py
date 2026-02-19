import uvicorn
from fastapi import FastAPI, BackgroundTasks
from vortex import VortexOmega  # Direct import works now because they are side-by-side

app = FastAPI(title="VORTEX V3.1.0 - FLAT DEPLOY")
vortex = VortexOmega()

@app.get("/health")
async def health():
    try:
        equity = await vortex.get_total_equity()
        return {
            "version": "3.1.0",
            "status": "ONLINE",
            "equity_usdt": equity,
            "mode": "FLAT_STRIKE"
        }
    except Exception as e:
        return {"status": "OFFLINE", "reason": str(e)}

@app.get("/strike/{side}/{symbol}")
async def strike(side: str, symbol: str):
    # Triggers the V3.1.0 automated 4% sizing trade
    return await vortex.execute_trade(symbol, side)

@app.get("/start/{symbol}")
async def start(symbol: str, tasks: BackgroundTasks):
    tasks.add_task(vortex.monitor_market, symbol)
    return {"message": f"Vortex V3.1.0 monitoring {symbol}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
