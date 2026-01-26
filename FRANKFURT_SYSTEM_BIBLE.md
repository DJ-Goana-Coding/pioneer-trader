# 🏛️ FRANKFURT CITADEL: SYSTEM BIBLE
**Archived:** 2026-01-15 16:43

This document contains the complete source code for the active T.I.A. system.

## 📄 requirements.txt
```python
fastapi
uvicorn
streamlit
ccxt
apscheduler
pandas
pandas_ta
numpy
pydantic
requests
python-multipart
python-dotenv
```

## 📄 start.sh
```python
#!/usr/bin/env bash
set -e
echo '🚀 STARTING FRANKFURT CITADEL...'
# Start Brain (Internal Port 8000)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
sleep 5
# Start Face (Public Port 7860/10000)
streamlit run streamlit_app/app.py --server.port 7860 --server.address 0.0.0.0

```

## 📄 render.yaml
```python
services:
  - type: web
    name: pioneer-trader
    env: python
    region: frankfurt
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: ./start.sh
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0

```

## 📄 Dockerfile
```python
FROM python:3.11-slim
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY --chown=user . .
EXPOSE 7860
CMD ["/bin/bash", "start.sh"]

```

## 📄 backend/core/config.py
```python
from pydantic import BaseModel
import os
class Settings(BaseModel):
    PROJECT_NAME: str = "Pioneer Trader"
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    BINANCE_SECRET_KEY: str = os.getenv("BINANCE_SECRET_KEY", "")
settings = Settings()

```

## 📄 backend/core/personas.py
```python
from typing import List, Optional
from pydantic import BaseModel

class Persona(BaseModel):
    id: str; name: str; role: str; style: str; triggers: List[str]

PERSONA_REGISTRY = {
    "TIA": Persona(id="TIA", name="T.I.A.", role="Captain", style="green", triggers=["status", "report", "tia", "system"]),
    "GOANNA": Persona(id="GOANNA", name="DJ Goanna", role="DJ", style="purple", triggers=["bass", "vibe", "play"]),
    "VOID": Persona(id="VOID", name="The Void", role="Oracle", style="red", triggers=["truth", "dark", "prediction"]),
    "HIPPY": Persona(id="HIPPY", name="Hippy", role="Guide", style="blue", triggers=["peace", "chill", "love"])
}
def detect_persona(text: str) -> Optional[Persona]:
    for _, p in PERSONA_REGISTRY.items():
        if any(t in text.lower() for t in p.triggers): return p
    return None

```

## 📄 backend/services/strategies.py
```python
import pandas_ta as ta
import pandas as pd
class StrategyLogic:
    def p25_momentum(self, df: pd.DataFrame) -> str:
        if df.empty or len(df) < 14: return "HOLD"
        rsi = df.ta.rsi(length=14).iloc[-1]
        if rsi < 30: return "BUY"
        if rsi > 70: return "SELL"
        return "HOLD"
    def golden_cross(self, df: pd.DataFrame) -> str:
        if df.empty or len(df) < 200: return "HOLD"
        s50 = df.ta.sma(length=50); s200 = df.ta.sma(length=200)
        if s50.iloc[-1] > s200.iloc[-1] and s50.iloc[-2] <= s200.iloc[-2]: return "BUY"
        return "HOLD"

```

## 📄 backend/services/vortex.py
```python
import asyncio
import ccxt.async_support as ccxt
import os
from backend.services.strategies import StrategyLogic

class Slot:
    def __init__(self, id):
        self.id = id; self.capital = 10.50; self.status = "IDLE"; self.asset = "None"

class VortexEngine:
    def __init__(self):
        self.slots = [Slot(i+1) for i in range(7)]
        self.logic = StrategyLogic()
        self.running = False
        self.exchange = None
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.secret = os.getenv("BINANCE_SECRET_KEY")

    async def _init_exchange(self):
        if not self.exchange and self.api_key:
            self.exchange = ccxt.binance({'apiKey': self.api_key, 'secret': self.secret, 'enableRateLimit': True})

    async def heartbeat(self):
        if not self.running: return
        await self._init_exchange()
        print(f"💓 Vortex Scanning {len(self.slots)} Slots...")
        for slot in self.slots:
            if slot.status == "IDLE": slot.status = "HUNTING"; slot.asset = "SCANNING..."

    async def start(self): self.running = True
    async def stop(self): self.running = False
    async def get_telemetry(self):
        return {"status": "RUNNING" if self.running else "STOPPED", "slots": [{"id": s.id, "status": s.status, "asset": s.asset} for s in self.slots]}

```

## 📄 backend/services/brain.py
```python
from backend.core.personas import PERSONA_REGISTRY, detect_persona
from backend.services.vortex import VortexEngine
from backend.services.knowledge import knowledge_base
class SkinWalkerBrain:
    def __init__(self):
        self.persona = PERSONA_REGISTRY["TIA"]
        self.vortex = VortexEngine()
    async def process(self, text: str):
        new_p = detect_persona(text)
        if new_p: self.persona = new_p
        if "learn" in text.lower():
            knowledge_base.save_fact(text)
            return {"msg": f"[{self.persona.name}] Learned.", "persona": self.persona.name}
        return {"msg": f"[{self.persona.name}] {text}", "persona": self.persona.name}
brain = SkinWalkerBrain()

```

## 📄 backend/services/knowledge.py
```python
import json
from pathlib import Path
from datetime import datetime
DB_PATH = Path("encyclopedia/knowledge_base.json")
class KnowledgeBase:
    def __init__(self):
        if not DB_PATH.exists():
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            DB_PATH.write_text(json.dumps({"facts": []}), encoding="utf-8")
    def save_fact(self, content: str):
        data = json.loads(DB_PATH.read_text())
        data["facts"].append({"content": content, "ts": datetime.utcnow().isoformat()})
        DB_PATH.write_text(json.dumps(data, indent=2))
knowledge_base = KnowledgeBase()

```

## 📄 backend/main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backend.services.brain import brain

scheduler = AsyncIOScheduler()
@asynccontextmanager
async def lifespan(app: FastAPI):
    await brain.vortex.start()
    scheduler.add_job(brain.vortex.heartbeat, 'interval', seconds=10)
    scheduler.start()
    yield
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

```

## 📄 streamlit_app/app.py
```python
import streamlit as st
import requests
import pandas as pd
st.set_page_config(page_title="Pioneer Trader", layout="wide")
API = "http://localhost:8000"
st.title("Pioneer Trader — Frankfurt Citadel")
col1, col2 = st.columns(2)
with col1:
    st.subheader("📡 Vortex Workers")
    if st.button("Refresh Telemetry"):
        try:
            data = requests.get(f"{API}/telemetry", timeout=3).json()
            st.metric("System Status", data["status"])
            st.dataframe(pd.DataFrame(data["slots"]), use_container_width=True)
        except: st.error("Backend Offline")
with col2:
    st.subheader("💬 T.I.A. Command")
    user_input = st.text_input("Execute Order / Switch Persona")
    if st.button("Send Command"):
        try:
            resp = requests.post(f"{API}/chat", json={"message": user_input}).json()
            st.success(resp["msg"])
            st.caption(f"Identity: {resp.get('persona')}")
        except: st.error("Comms Failure")

```
