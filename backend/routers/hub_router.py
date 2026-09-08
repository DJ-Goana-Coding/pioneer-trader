"""Hub router — links this Citadel node to the central Hub.

Exposes two endpoints under ``/v1``:

* ``POST /v1/ingest`` — forwards payloads to the Hub's ingestion endpoint
  so that fragments from this node are added to the global FAISS vector
  store.
* ``POST /v1/query`` — forwards a query to the Hub and returns the Hub's
  RAG response.

The target Hub URL is read from the ``MAPPING_HUB_URL`` environment
variable. It defaults to the ``DJ-Goana-Coding/Mapping-and-Inventory``
Hugging Face Space, which is the documented home of the global vector
store.

The router intentionally keeps logic minimal: it is a thin synapse, not
a re-implementation of the Hub.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request

logger = logging.getLogger(__name__)

DEFAULT_HUB_URL = "https://dj-goana-coding-mapping-and-inventory.hf.space"
HUB_URL = os.environ.get("MAPPING_HUB_URL", DEFAULT_HUB_URL).rstrip("/")
HUB_TIMEOUT_SECONDS = float(os.environ.get("MAPPING_HUB_TIMEOUT", "30"))

router = APIRouter(prefix="/v1", tags=["hub"])


async def _forward(path: str, payload: Any) -> Any:
    """Forward ``payload`` to ``{HUB_URL}{path}`` and return the JSON body."""
    url = f"{HUB_URL}{path}"
    try:
        async with httpx.AsyncClient(timeout=HUB_TIMEOUT_SECONDS) as client:
            response = await client.post(url, json=payload)
    except httpx.HTTPError as exc:
        logger.warning("Hub request to %s failed: %s", url, exc)
        raise HTTPException(status_code=502, detail=f"Hub unreachable: {exc}") from exc

    if response.status_code >= 400:
        logger.warning(
            "Hub returned %s for %s: %s", response.status_code, url, response.text[:200]
        )
        raise HTTPException(status_code=response.status_code, detail=response.text)

    try:
        return response.json()
    except json.JSONDecodeError:
        return {"raw": response.text}


@router.get("/hub/health")
async def hub_health() -> dict[str, str]:
    """Report which Hub URL this node is welded to."""
    return {"hub_url": HUB_URL, "status": "configured"}


@router.post("/ingest")
async def ingest(request: Request) -> Any:
    """Forward an ingestion payload to the Hub's FAISS store."""
    payload = await request.json()
    return await _forward("/v1/ingest", payload)


@router.post("/query")
async def query(request: Request) -> Any:
    """Forward a RAG query to the Hub and return the Hub's response."""
    payload = await request.json()
    return await _forward("/v1/query", payload)
