from fastapi import FastAPI, HTTPException, Header
from backend.services.vortex import VortexBerserker
import asyncio
import os

app = FastAPI(title="T.I.A. Pioneer Trader")
bot = VortexBerserker()

@app.on_event("startup")
async def startup_event():
    # Launches the bot as a non-blocking background task
    asyncio.create_task(bot.start())

@app.get("/health")
async def health():
    """Live Heartbeat for Render and User"""
    return {"status": "online", "bot_data": bot.get_status()}

@app.post("/omega-stop")
async def kill_switch(auth: str = Header(None)):
    """Secure Emergency Stop"""
    if auth != os.getenv("KILL_AUTH_TOKEN"):
        raise HTTPException(status_code=403, detail="Unauthorized")
    await bot.stop_engine()
    return {"message": "Shutdown initiated."}

@app.get("/")
async def root():
    return {"message": "T.I.A. Node Active. Visit /health for status."}