import uvicorn
from fastapi import FastAPI, BackgroundTasks
from vortex import VortexOmega

app = FastAPI()
vortex = VortexOmega()

@app.get("/health")
async def health():
    balance = await vortex.get_balance()
    return {"status": "ONLINE", "balance": balance['total'].get('USDT', 0)}

@app.get("/strike/{side}/{symbol}/{amount}")
async def manual_strike(side: str, symbol: str, amount: float):
    # API Hook for instant trades: /strike/buy/BTC_USDT/0.001
    return await vortex.execute_trade(symbol, side, amount)

@app.get("/start/{symbol}")
async def start_vortex(symbol: str, tasks: BackgroundTasks):
    # API Hook to start the live monitor: /start/BTC_USDT
    tasks.add_task(vortex.monitor_market, symbol)
    return {"message": f"Vortex monitoring {symbol} initiated."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
