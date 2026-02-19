import uvicorn
from fastapi import FastAPI, BackgroundTasks
from vortex import VortexOmega  # Direct import works now as they are side-by-side

app = FastAPI(title="CGAL OMEGA TRADER")
vortex = VortexOmega()

@app.get("/health")
async def health():
    try:
        balance = await vortex.get_balance()
        return {
            "status": "ONLINE", 
            "usdt_total": balance['total'].get('USDT', 0),
            "usdt_free": balance['free'].get('USDT', 0)
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@app.get("/strike/{side}/{symbol}/{amount}")
async def manual_strike(side: str, symbol: str, amount: float):
    # Example: /strike/buy/BTC_USDT/0.001
    return await vortex.execute_trade(symbol, side, amount)

@app.get("/start/{symbol}")
async def start_vortex(symbol: str, tasks: BackgroundTasks):
    # Example: /start/BTC_USDT
    tasks.add_task(vortex.monitor_market, symbol)
    return {"message": f"Vortex monitoring {symbol} initiated."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
