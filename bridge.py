import os
import json
import asyncio
import logging
import zmq
import zmq.asyncio
import duckdb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime, timezone

app = FastAPI(title="Citadel C2 Nexus Router", version="20.5.0")

ZMQ_HOST = os.getenv("ZERO_MQ_HOST", "127.0.0.1")
ZMQ_PORT = os.getenv("ZERO_MQ_PORT", "5557")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
DUCKDB_PATH = os.getenv("DUCKDB_PATH", r"D:\citadel_memory.duckdb")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("citadel_bridge")

ctx = zmq.asyncio.Context()
zmq_socket = ctx.socket(zmq.PUSH)
zmq_socket.setsockopt(zmq.SNDTIMEO, 3000)
zmq_socket.setsockopt(zmq.LINGER, 0)
zmq_socket.connect(f"tcp://{ZMQ_HOST}:{ZMQ_PORT}")

try:
    db = duckdb.connect(DUCKDB_PATH, read_only=True)
except Exception:
    logger.exception("DuckDB read-only connect failed: %s", DUCKDB_PATH)
    db = None


async def _send_to_gateway(payload: dict) -> None:
    try:
        await zmq_socket.send_string(json.dumps(payload, ensure_ascii=False))
    except zmq.ZMQError as exc:
        logger.error("ZMQ send failed on port %s: %s", ZMQ_PORT, exc)
        raise HTTPException(status_code=503, detail=f"ZMQ gateway send failed: {exc}") from exc

class WeightVector(BaseModel):
    source_agent: str
    target_weights: Dict[str, float]
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class OrderIntent(BaseModel):
    side: str = Field(..., pattern="^(buy|sell)$")
    symbol: str
    quantity: float
    order_type: str = Field(default="market")
    metadata: Optional[Dict[str, Any]] = None

@app.get("/v1/system/status")
async def get_system_status():
    agent_count = 0
    if db:
        try:
            res = db.execute("SELECT COUNT(*) FROM sovereign_constellation").fetchone()
            agent_count = res[0] if res else 0
        except Exception:
            logger.exception("sovereign_constellation count query failed")
    return {
        "status": "OMEGA-STAINLESS",
        "district": "D01",
        "dry_run_active": DRY_RUN,
        "active_agents_in_ledger": agent_count,
        "storage_root": os.path.dirname(DUCKDB_PATH),
        "duckdb_connected": db is not None,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/v1/weights")
async def ingest_weights(vector: WeightVector):
    payload = {"district": "D01", "event": "TARGET_WEIGHTS_UPDATE", "payload": vector.model_dump()}
    await _send_to_gateway(payload)
    return {"status": "accepted", "vector": vector.source_agent}

@app.post("/v1/order_intent")
async def process_order_intent(intent: OrderIntent):
    event_type = "ORDER_INTENT_DRY_RUN" if DRY_RUN else "ORDER_INTENT_LIVE"
    payload = {"district": "D01", "event": event_type, "payload": intent.model_dump()}
    await _send_to_gateway(payload)
    if DRY_RUN:
        return {"status": "dry_run_logged", "action": "bypassed_execution"}
    return {"status": "routed_to_execution", "symbol": intent.symbol}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bridge:app", host="127.0.0.1", port=8000, reload=False)
