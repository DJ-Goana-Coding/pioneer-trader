import uvicorn
from fastapi import FastAPI, BackgroundTasks, UploadFile, File
from vortex import VortexOmega

app = FastAPI(title="CGAL OMEGA")
vortex = VortexOmega()

@app.get("/health")
async def health():
    balance = await vortex.get_balance()
    return {
        "status": "VORTEX_ONLINE",
        "mexc_connection": "ESTABLISHED",
        "usdt_balance": balance['total'].get('USDT', 0)
    }

@app.get("/strike/{side}/{symbol}/{amount}")
async def manual_strike(side: str, symbol: str, amount: float):
    # Instant MEXC Market Order
    return await vortex.execute_trade(symbol, side, amount)

@app.get("/start/{symbol}")
async def start_vortex(symbol: str, tasks: BackgroundTasks):
    # Initiate Background Monitor
    tasks.add_task(vortex.monitor_market, symbol)
    return {"message": f"Vortex Omega monitoring {symbol}"}

@app.post("/upload-ledger")
async def upload_ledger(file: UploadFile = File(...)):
    # Reinstating the file upload capability
    return {"filename": file.filename, "status": "LOGGED_TO_LEDGER"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
