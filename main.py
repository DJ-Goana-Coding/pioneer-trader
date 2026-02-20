from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import os
import vortex  # Assuming your logic is in vortex.py

app = FastAPI()

# 1. THE FRONTEND: This serves your HTML file at the root URL
@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    with open("index.html", "r") as f:
        return f.read()

# 2. THE FUEL: This provides the JSON data your dashboard's JS is looking for
@app.get("/api/data")
async def get_data():
    return {
        "balance": getattr(vortex, 'total_balance', 0.0),
        "profit_total": getattr(vortex, 'total_profit', "0.00"),
        "portfolio": getattr(vortex, 'active_trades', {}),
        "strategies": vortex.get_strategy_status() if hasattr(vortex, 'get_strategy_status') else []
    }

# Your existing Ignition Block
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 CITADEL IGNITION ON PORT {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
