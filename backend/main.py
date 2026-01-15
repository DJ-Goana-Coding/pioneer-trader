from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backend.services.brain import brain

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # START AUTOMATION
    await brain.vortex.start()
    scheduler.add_job(brain.vortex.heartbeat, 'interval', seconds=10)
    scheduler.start()
    yield
    # STOP AUTOMATION
    await brain.vortex.stop()

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class ChatReq(BaseModel): message: str

@app.get("/")
async def root(): return {"status": "Frankfurt Citadel Online"}

@app.get("/telemetry")
async def telemetry(): return await brain.vortex.get_telemetry()

@app.post("/chat")
async def chat(r: ChatReq): return await brain.process(r.message)